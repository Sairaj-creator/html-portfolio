from pydantic import BaseModel, Field
from typing import Literal, List, Any

QueryType = Literal["STRUCTURED", "UNSTRUCTURED", "HYBRID"]


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1)
    user_id: str
    session_id: str


class QueryResponse(BaseModel):
    query: str
    response: str
    query_type: QueryType
    sources: List[str]
    cached: bool
    execution_time_ms: int


class StructuredPayload(BaseModel):
    answer: str
    sql_executed: str
    row_count: int
    source_tables: List[str]


class UnstructuredPayload(BaseModel):
    answer: str
    sources: List[str]
    confidence_score: float
    chunks_used: List[Any]
