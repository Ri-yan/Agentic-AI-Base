# analytics_platform/models/query_config_model.py
from typing import Optional
from pydantic import BaseModel

class QueryConfig(BaseModel):
    query: str
    user_id: Optional[str] = None
