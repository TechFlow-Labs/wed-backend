from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class NoteCreateSchema(BaseModel):
    content: str
    reservation_id: Optional[UUID] = None

class NoteUpdateSchema(BaseModel):
    content: Optional[str] = None
    reservation_id: Optional[UUID] = None


class NoteReservationsSchema(BaseModel):
    id: UUID
    author_id: UUID
    content: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NoteResponseSchema(BaseModel):
    id: UUID
    author_id: UUID
    reservation_id: Optional[UUID] = None
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)