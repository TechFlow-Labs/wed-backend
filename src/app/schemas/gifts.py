from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class GiftDashboard(BaseModel):
    id: UUID
    item_name: str
    category: Optional[str]
    short_description: Optional[str]
    long_description: Optional[str]
    main_image_url: Optional[str]
    gallery_image_urls: List[str]

    class Config:
        from_attributes = True


class GiftCreate(BaseModel):
    item_name: str
    category: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    main_image_url: Optional[str] = None
    gallery_image_urls: List[str] = []
