from pydantic import BaseModel

class ProcessPDFRequest(BaseModel):
    file_path: str
    api_key: str 
    
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    context: str

