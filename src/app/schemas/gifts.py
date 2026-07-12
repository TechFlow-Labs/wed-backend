from pydantic import BaseModel, field_validator
from uuid import UUID
from typing import List, Optional

class GiftDashboard(BaseModel):
    id: UUID
    item_name: str
    category: Optional[str]
    short_description: Optional[str]
    long_description: Optional[str]
    main_image_url: Optional[str]
    gallery_image_urls: List[str] = []

    @field_validator("gallery_image_urls", mode="before")
    @classmethod
    def none_to_empty_list(cls, value: List[str] | None) -> List[str]:
        return value if value is not None else []

    class Config:
        from_attributes = True


class GiftCreate(BaseModel):
    item_name: str
    category: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    main_image_url: Optional[str] = None
    gallery_image_urls: List[str] = []
