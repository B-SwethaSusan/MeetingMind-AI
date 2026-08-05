from pydantic import BaseModel, Field


class TranscriptRequest(BaseModel):
    transcript: str = Field(min_length=1)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
