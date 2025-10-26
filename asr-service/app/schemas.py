from typing import List

from pydantic import BaseModel, Field


class Segment(BaseModel):
    start_ms: int = Field(..., example=0)
    end_ms: int = Field(..., example=2000)
    text: str = Field(..., example="Hello world")


class STTResponse(BaseModel):
    text: str
    segments: List[Segment]
