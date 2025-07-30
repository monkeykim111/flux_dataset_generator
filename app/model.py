from pydantic import BaseModel

class GenerateRequest(BaseModel):
    trigger_word: str
    index: int

