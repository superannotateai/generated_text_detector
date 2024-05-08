from pydantic import BaseModel

from generated_text_detector.utils.author import Author


class TextRequest(BaseModel):
    text: str


class ReportResponse(BaseModel):
    generated_score: float
    author: Author
