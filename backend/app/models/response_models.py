"""Structured JSON returned by meeting analysis."""

from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    task: str = Field(description="The work that must be completed")
    assignee: str = Field(description="Person responsible for the task")
    deadline: str = Field(default="Not Mentioned")
    priority: str = Field(description="High, Medium, or Low")


class MeetingAnalysis(BaseModel):
    meeting_date: str = Field(default="Not Mentioned")
    department: str = Field(default="Not Mentioned")
    action_items: list[ActionItem] = Field(default_factory=list)


class ChatAnswer(BaseModel):
    answer: str
    evidence: str = Field(
        default="",
        description="An exact, verbatim quote from the transcript supporting the answer",
    )
