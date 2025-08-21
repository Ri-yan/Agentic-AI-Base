from pydantic import BaseModel
class AgentQuery(BaseModel):
    sessionId:str
    prompt: str
    payload:dict