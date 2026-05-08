from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class GuestDashboard(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: Optional[str]
    phone_number: Optional[str]
    reservation_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

class GuestCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    reservation_id: Optional[UUID] = None
