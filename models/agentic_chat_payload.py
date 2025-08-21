from typing import Optional, Dict, Any
from pydantic import BaseModel

from api.models.base_payload import BasePayload

class AgenticChatPayload(BasePayload):
    sessionId:str