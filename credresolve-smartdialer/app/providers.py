import random,uuid
class ProviderError(Exception): pass
class MockProvider:
    def __init__(self,name,failure_rate=0,duplicate=False,out_of_order=False):
        self.name=name; self.failure_rate=failure_rate; self.duplicate=duplicate; self.out_of_order=out_of_order
    def start_call(self,borrower_id):
        if random.random()<self.failure_rate: raise ProviderError("simulated provider timeout")
        return {"provider_call_id":self.name+"-"+uuid.uuid4().hex[:10]}
    def events_for(self,call_id):
        e=[{"event_id":call_id+"-ring","call_id":call_id,"status":"RINGING"},
           {"event_id":call_id+"-answer","call_id":call_id,"status":"ANSWERED"},
           {"event_id":call_id+"-complete","call_id":call_id,"status":"COMPLETED"}]
        if self.out_of_order: e.reverse()
        if self.duplicate: e.insert(1,e[0].copy())
        return e
class ProviderA(MockProvider):
    def __init__(self): super().__init__("provider_a",.02)
class ProviderB(MockProvider):
    def __init__(self): super().__init__("provider_b",.15,True,True)
