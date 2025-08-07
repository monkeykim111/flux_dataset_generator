from pydantic import BaseModel
from typing import Optional

class GenerateRequest(BaseModel):
    generation_mode: str = "shot_type"  # Default to 'shot_type' for backward compatibility
    trigger_word: str
    character_name: str
    index: int
    expression: Optional[str] = None
    angle: Optional[str] = None
