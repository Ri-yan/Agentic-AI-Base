from pydantic import BaseModel
from typing import Optional


class SchemaDetails(BaseModel):
    table_name: str
    db_type: str
    fields: Optional[str] = ""


class AGPT_GenerationPayload(BaseModel):
    schema_details: SchemaDetails
    query: str
