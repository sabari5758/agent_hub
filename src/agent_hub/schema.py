from pydantic import BaseModel, Field
from typing import List, Optional

# Request: What the user sends
class TrendRequest(BaseModel):
    topic: str = Field(..., example="AI in Frontend")
    platform: str = Field(default="X.com")

# Response: What the API returns (Structured)
class TechTrend(BaseModel):
    title: str
    summary: str
    source_url: Optional[str]
    img: Optional[str]

class TrendResponse(BaseModel):
    trends: List[TechTrend]
    status: str

class JobOpening(BaseModel):
    """Schema for an individual frontend job opening."""
    title: str = Field(..., description="The job title (e.g., Senior React Developer)")
    summary: str = Field(..., description="A 1-2 sentence description of the role and requirements")
    img: Optional[str] = Field(None, description="A placeholder or actual URL for a company logo or tech icon")
    url: str = Field(..., description="The direct link to the job application or posting")

class JobBoardResponse(BaseModel):
    """Container schema for the list of job openings."""
    jobs: List[JobOpening] = Field(..., description="A list of 5 to 10 frontend job openings")
    topic: str = Field(..., description="The specific frontend topic researched")