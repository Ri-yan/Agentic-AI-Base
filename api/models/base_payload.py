from typing import Dict, Any, Optional

from pydantic import BaseModel

class BasePayload(BaseModel):
    prompt: str
    payload:Optional[Dict[str, Any]]
    additional_data:Optional[Any]