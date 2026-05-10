from typing import List
from pydantic import BaseModel, Field


class SpecialPartnerSchema(BaseModel):
    # Public mock contract used by frontend SSR and Expo clients.
    id: str = Field(..., description="Unique partner id")
    name: str = Field(..., description="Partner display name")
    category: str = Field(..., description="Partner category")
    city: str = Field(..., description="Partner city")
    shortDescription: str = Field(..., description="Short summary")
    badge: str = Field(..., description="Highlight badge label")
    featuredImage: str = Field(..., description="Featured card image URL")
    rating: float = Field(..., description="Rating from 0 to 5")


class SpecialPartnersResponse(BaseModel):
    items: List[SpecialPartnerSchema]
