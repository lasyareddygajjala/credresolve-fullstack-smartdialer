from fastapi import FastAPI,HTTPException
from .engine import Dialer
from .models import DialRequest
app=FastAPI(title="CredResolve SmartDialer")
dialer=Dialer()
for i in range(1,6):dialer.store.add_agent(f"agent-{i}")
for i in range(1,31):dialer.store.add_borrower(f"borrower-{i}")
@app.get("/")
def root():return {"message":"SmartDialer prototype","docs":"/docs"}
@app.get("/state")
def state():
 s=dialer.store
 return {"agents":[x.model_dump() for x in s.agents.values()],"borrowers":[x.model_dump() for x in s.borrowers.values()],"calls":[x.model_dump() for x in s.calls.values()]}
@app.post("/dial")
def dial(req:DialRequest,provider:str="provider_a"):
 if provider not in dialer.providers:raise HTTPException(400,"Unknown provider")
 return dialer.dial(req.mode,req.answer_rate,req.max_extra_calls,provider)
@app.post("/events")
def events(payload:dict):
 if not {"event_id","call_id","status"}.issubset(payload):raise HTTPException(400,"event_id, call_id, status required")
 try:return dialer.process_event(payload)
 except ValueError as e:raise HTTPException(400,str(e))
