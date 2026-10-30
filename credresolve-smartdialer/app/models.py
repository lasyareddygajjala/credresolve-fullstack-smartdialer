from enum import Enum
from pydantic import BaseModel,Field
class AgentStatus(str,Enum):
    OFFLINE="OFFLINE"; AVAILABLE="AVAILABLE"; RESERVED="RESERVED"; DIALING="DIALING"; CONNECTED="CONNECTED"; WRAP_UP="WRAP_UP"; PAUSED="PAUSED"
class CallStatus(str,Enum):
    QUEUED="QUEUED"; RESERVED="RESERVED"; INITIATED="INITIATED"; RINGING="RINGING"; ANSWERED="ANSWERED"; CONNECTED="CONNECTED"; COMPLETED="COMPLETED"; FAILED="FAILED"; CANCELLED="CANCELLED"
class Agent(BaseModel):
    agent_id:str
    status:AgentStatus=AgentStatus.AVAILABLE
class Borrower(BaseModel):
    borrower_id:str
    status:str="QUEUED"
class Call(BaseModel):
    call_id:str; borrower_id:str; agent_id:str; provider:str
    status:CallStatus=CallStatus.RESERVED
    provider_call_id:str|None=None
    version:int=0
class DialRequest(BaseModel):
    mode:str=Field("progressive",pattern="^(progressive|predictive)$")
    answer_rate:float=Field(.35,ge=.01,le=.99)
    max_extra_calls:int=Field(10,ge=0,le=100)
