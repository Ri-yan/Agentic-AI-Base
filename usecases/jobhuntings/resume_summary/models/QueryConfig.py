from pydantic import BaseModel, Field
from typing import Literal

class QueryConfigModel(BaseModel):
    isValidQuery: bool
    multiResponse: bool
    type: str
    intent: str
    topic: str
    urgency: str
    requiresAuth: bool
    fieldsMentioned: bool
    language: str  # Ideally ISO 2-letter codes
    messageResponse: str
    widgetType: str