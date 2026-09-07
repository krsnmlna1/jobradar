from datetime import datetime

from pydantic import BaseModel


class JobIn(BaseModel):
    source: str
    ext_id: str
    title: str
    company: str
    url: str
    description: str | None = None
    location: str | None = None
    posted_at: datetime | None = None


class JobSummary(BaseModel):
    id: int
    title: str
    company: str
    location: str | None = None
    posted_at: datetime | None = None


class JobDetail(JobSummary):
    source: str
    ext_id: str
    url: str
    description: str | None = None
    ingested_at: datetime
