from pydantic import BaseModel
from typing import List, Optional

class UploadResponse(BaseModel):
    job_id: str
    filename: str

class Segment(BaseModel):
    start: float
    end: float
    text: str
    speaker: Optional[int] = None

class TranscriptionResponse(BaseModel):
    segments: List[Segment]
