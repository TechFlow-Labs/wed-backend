from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from typing import List, Optional


class WebsiteFaqItem(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)


class WebsiteScheduleItem(BaseModel):
    time: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: Optional[str] = None


class WeddingWebsiteGenerateRequest(BaseModel):
    slug: str = Field(min_length=3, max_length=64, pattern=r"^[a-z0-9-]+$")
    couple_names: str = Field(min_length=2, max_length=120)
    wedding_date: date
    venue: str = Field(min_length=2, max_length=200)
    story: Optional[str] = None
    schedule: List[WebsiteScheduleItem] = []
    faq: List[WebsiteFaqItem] = []


class WeddingWebsiteResponse(BaseModel):
    slug: str
    couple_names: str
    wedding_date: date
    venue: str
    story: Optional[str] = None
    schedule: List[WebsiteScheduleItem]
    faq: List[WebsiteFaqItem]
    rsvp_enabled: bool = True
    rsvp_deadline: Optional[date] = None
    public_path: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
