from pydantic import BaseModel

class GenerateRequest(BaseModel):
    trigger_word: str
    character_name: str
    index: int

