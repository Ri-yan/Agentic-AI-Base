from pydantic import BaseModel, validator, ValidationError, Field
from typing import List, Optional, Literal

#Filter
class FieldDefinition(BaseModel):
    FieldName: str
    FieldType: str
    Type: Optional[str] = None
    Aggregation: Optional[str] = None

#Field
class FilterDefinition(BaseModel):
    FieldName: str
    FieldType: str
    Type: Optional[str] = None
    OperatorType: str
    Value: str

    @validator('OperatorType')
    def validate_operator(cls, v):
        allowed = {"Equal", "NotEqual", "NotIn", "In"}
        if v not in allowed:
            raise ValueError("Currently we only support Equals,NotEqual,NotIn and In operators")
        return v

class OrderDefinition(BaseModel):
    FieldName: str
    OrderType: Literal["ASC", "DESC"]

#SchemaModel
class SchemaModelOutput(BaseModel):
    Fields: List[FieldDefinition]
    Filters: List[FilterDefinition]
    GroupBy: List[str] = Field(default_factory=list)
    OrderBy: List[OrderDefinition]
    BatchSize: Optional[int] = None
    RoundUpCount: Optional[int] = None
