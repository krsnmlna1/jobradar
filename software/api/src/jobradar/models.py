"""Model Pydantic — batas validasi antara dunia luar dan database."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class JobIn(BaseModel):
    """Lowongan mentah yang masuk dari sebuah channel."""

    source: str = Field(
        min_length=1, max_length=64, description="mis. indeed, rwfa, linkedin"
    )
    ext_id: str = Field(min_length=1, max_length=255, description="id di sistem asal")
    title: str = Field(min_length=1, max_length=512)
    company: str = Field(min_length=1, max_length=255)
    url: HttpUrl
    location: str | None = Field(default=None, max_length=255)
    posted_at: datetime | None = None


class Job(JobIn):
    """Lowongan sebagaimana tersimpan."""

    id: int
    ingested_at: datetime


class Health(BaseModel):
    status: str
    database: str
