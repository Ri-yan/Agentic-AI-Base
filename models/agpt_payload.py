from typing import Optional, Dict, Any
from pydantic import BaseModel

from api.models.base_payload import BasePayload


class AGPT_Payload(BasePayload):
    table_name:Optional[Any]
    db_type:Optional[Any]
    fields:Optional[Any]