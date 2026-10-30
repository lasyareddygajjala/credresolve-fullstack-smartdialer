from threading import RLock
from uuid import uuid4
from .models import Agent,Borrower,Call,AgentStatus,CallStatus
from .providers import ProviderA,ProviderB,ProviderError
LEGAL={CallStatus.RESERVED:{CallStatus.INITIATED,CallStatus.FAILED,CallStatus.CANCELLED},
 CallStatus.INITIATED:{CallStatus.RINGING,CallStatus.ANSWERED,CallStatus.FAILED,CallStatus.CANCELLED},
 CallStatus.RINGING:{CallStatus.ANSWERED,CallStatus.FAILED,CallStatus.CANCELLED},
 CallStatus.ANSWERED:{CallStatus.CONNECTED,CallStatus.COMPLETED},
 CallStatus.CONNECTED:{CallStatus.COMPLETED}}
class Store:
    def __init__(self):
        self.lock=RLock(); self.agents={}; self.borrowers={}; self.calls={}; self.events=set()
    def add_agent(self,x):
        with self.lock:self.agents[x]=Agent(agent_id=x)
    def add_borrower(self,x):
        with self.lock:self.borrowers[x]=Borrower(borrower_id=x)
class PredictivePacingEngine:
    def propose(self,free_agents,answer_rate,max_extra_calls):
        if free_agents<=0:return 0
        expected_answers=int(free_agents*.8)
        return min(int(expected_answers/max(answer_rate,.01)),free_agents+max_extra_calls)
class SafetyController:
    def __init__(self,store,hard_cap=100):self.store=store;self.hard_cap=hard_cap
    def approve(self,proposed):
        with self.store.lock:
            free=sum(a.status==AgentStatus.AVAILABLE for a in self.store.agents.values())
            queued=sum(b.status=="QUEUED" for b in self.store.borrowers.values())
            return max(0,min(proposed,free,queued,self.hard_cap))
class Dialer:
    def __init__(self,store=None):
        self.store=store or Store(); self.pacing=PredictivePacingEngine(); self.safety=SafetyController(self.store)
        self.providers={"provider_a":ProviderA(),"provider_b":ProviderB()}
    def dial(self,mode="progressive",answer_rate=.35,max_extra_calls=10,provider_name="provider_a"):
        with self.store.lock:
            free=sum(a.status==AgentStatus.AVAILABLE for a in self.store.agents.values())
            queued=sum(b.status=="QUEUED" for b in self.store.borrowers.values())
            proposed=min(free,queued) if mode=="progressive" else min(queued,self.pacing.propose(free,answer_rate,max_extra_calls))
            approved=self.safety.approve(proposed); started=[]
            provider=self.providers[provider_name]
            for _ in range(approved):
                agent=next((x for x in self.store.agents.values() if x.status==AgentStatus.AVAILABLE),None)
                borrower=next((x for x in self.store.borrowers.values() if x.status=="QUEUED"),None)
                if not agent or not borrower:break
                agent.status=AgentStatus.RESERVED; borrower.status="RESERVED"
                call=Call(call_id=uuid4().hex,borrower_id=borrower.borrower_id,agent_id=agent.agent_id,provider=provider_name)
                self.store.calls[call.call_id]=call
                try:
                    call.provider_call_id=provider.start_call(borrower.borrower_id)["provider_call_id"]
                    call.status=CallStatus.INITIATED; agent.status=AgentStatus.DIALING
                except ProviderError:
                    call.status=CallStatus.FAILED; agent.status=AgentStatus.AVAILABLE; borrower.status="QUEUED"
                started.append(call.model_dump())
            return {"mode":mode,"proposed":proposed,"approved":approved,"started":len(started),"calls":started}
    def process_event(self,event):
        with self.store.lock:
            if event["event_id"] in self.store.events:return {"applied":False,"reason":"duplicate"}
            self.store.events.add(event["event_id"])
            call=self.store.calls.get(event["call_id"])
            if call is None:return {"applied":False,"reason":"unknown_call"}
            target=CallStatus(event["status"])
            if target not in LEGAL.get(call.status,set()):
                return {"applied":False,"reason":f"invalid_transition:{call.status}->{target}"}
            call.status=target; call.version+=1
            agent=self.store.agents[call.agent_id]; borrower=self.store.borrowers[call.borrower_id]
            if target in {CallStatus.ANSWERED,CallStatus.CONNECTED}:
                agent.status=AgentStatus.CONNECTED; borrower.status="IN_CALL"
            elif target==CallStatus.RINGING:agent.status=AgentStatus.DIALING
            elif target in {CallStatus.COMPLETED,CallStatus.FAILED,CallStatus.CANCELLED}:
                agent.status=AgentStatus.WRAP_UP; borrower.status="CONTACTED" if target==CallStatus.COMPLETED else "QUEUED"
            return {"applied":True,"call":call.model_dump()}
