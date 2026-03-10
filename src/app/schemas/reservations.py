from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from decimal import Decimal



class ReservationsSchema(BaseModel):
    id: UUID

    partner_id: UUID
    business_name: Optional[str] = None

    couple_id: Optional[UUID] = None
    couple_first_name: Optional[str] = None
    couple_last_name: Optional[str] = None

    guest_first_name: Optional[str]
    guest_last_name: Optional[str]
    guest_email: Optional[str]
    guest_phone: Optional[str]

    status: Optional[str]
    event_date: Optional[datetime]
    details: Optional[str]
    budget_per_reservation: Optional[Decimal]

    model_config = ConfigDict(from_attributes=True)