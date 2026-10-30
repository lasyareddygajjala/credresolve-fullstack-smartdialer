from app.engine import Dialer, Store
from app.models import AgentStatus, CallStatus

def build():
    s = Store()
    for i in range(3): s.add_agent(f"a{i}")
    for i in range(12): s.add_borrower(f"b{i}")
    return Dialer(s)

def test_progressive_capacity():
    d=build(); r=d.dial()
    assert r["started"] <= 3
    assert sum(a.status == AgentStatus.AVAILABLE for a in d.store.agents.values()) == 0

def test_predictive_safety_cap():
    d=build(); r=d.dial("predictive", .2, 50)
    assert r["approved"] <= 3

def test_unique_agent_and_borrower_reservations():
    d=build(); r=d.dial("predictive", .2, 50)
    assert len({c["agent_id"] for c in r["calls"]}) == r["started"]
    assert len({c["borrower_id"] for c in r["calls"]}) == r["started"]

def test_duplicate_event():
    d=build(); c=d.dial()["calls"][0]
    e={"event_id":"e1","call_id":c["call_id"],"status":"RINGING"}
    assert d.process_event(e)["applied"]
    assert d.process_event(e)["reason"] == "duplicate"

def test_out_of_order_terminal_rejected():
    d=build(); c=d.dial()["calls"][0]
    e={"event_id":"e2","call_id":c["call_id"],"status":"COMPLETED"}
    assert not d.process_event(e)["applied"]

def test_happy_path_transitions():
    d=build(); c=d.dial()["calls"][0]
    for status in ["RINGING", "ANSWERED", "CONNECTED", "COMPLETED"]:
        r=d.process_event({"event_id":"e-"+status,"call_id":c["call_id"],"status":status})
        assert r["applied"], r
    assert d.store.calls[c["call_id"]].status == CallStatus.COMPLETED
