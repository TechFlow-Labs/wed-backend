from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from decimal import Decimal
from schemas.guests import GuestDashboard
from schemas.notes import NoteReservationsSchema

class ReservationsItemSchema(BaseModel):
    id: UUID
    partner_id: UUID
    couple_id: Optional[UUID] = None
    guest_first_name: Optional[str] = None
    guest_last_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None
    status: Optional[str] = None
    event_date: Optional[datetime] = None
    details: Optional[str] = None
    budget_per_reservation: Optional[Decimal] = None
    interested_dates: Optional[str] = None
    guest_count: Optional[int] = None
    event_type: Optional[str] = None
    other_comments: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ReservationsSchema(ReservationsItemSchema):
    business_name: Optional[str] = None
    couple_first_name: Optional[str] = None
    couple_last_name: Optional[str] = None

    guests: List[GuestDashboard] = []
    notes: List[NoteReservationsSchema] = []

class ReservationsUpdateSchema(BaseModel):
    status: Optional[str] = None
    event_date: Optional[datetime] = None
    details: Optional[str] = None
    budget_per_reservation: Optional[Decimal] = None

class ReservationAcceptedCreateSchema(BaseModel):
    guest_first_name: str  
    guest_last_name: str   
    guest_email: str       
    guest_phone: Optional[str] = None
    event_date: Optional[datetime] = None
    details: Optional[str] = None
    budget_per_reservation: Optional[Decimal] = None
    interested_dates: Optional[str] = None
    guest_count: Optional[int] = None
    event_type: Optional[str] = None
    other_comments: Optional[str] = None

class ReservationPendingCreateGuestSchema(ReservationAcceptedCreateSchema):
    partner_id: UUID

class ReservationPendingCreateSchema(BaseModel):
    partner_id: UUID
    event_date: Optional[datetime] = None
    details: Optional[str] = None
    budget_per_reservation: Optional[Decimal] = None
