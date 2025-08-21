from typing import Dict, Any
from pydantic import BaseModel

class GenericToolInput(BaseModel):
    prompt: str
    payload: Dict[str, Any] = {}