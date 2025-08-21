# analytics_platform/models/schemas.py
from pydantic import BaseModel

class AnalyticsRequest(BaseModel):
    query: str

class AnalyticsResponse(BaseModel):
    result: str
