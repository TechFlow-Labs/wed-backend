from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional, List

class VendorPublicSchema(BaseModel):
    partner_id: UUID
    business_name: str
    category: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class VendorListResponse(BaseModel):
    total: int
    items: List[VendorPublicSchema]