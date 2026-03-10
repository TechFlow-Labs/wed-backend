from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.db import Base 

class Reservations(Base):

    __tablename__ = "reservations"
    __table_args__ = {"schema": "weddingplan"} 

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id = Column(UUID(as_uuid=True), ForeignKey("weddingplan.users.id", ondelete="CASCADE"), nullable=False)
    couple_id = Column(UUID(as_uuid=True), ForeignKey("weddingplan.users.id", ondelete="CASCADE"), nullable=True)
    guest_first_name = Column(String(100), nullable=True)
    guest_last_name = Column(String(100), nullable=True)
    guest_email = Column(String(255), nullable=True)
    guest_phone = Column(String(50), nullable=True)
    status = Column(String(50), server_default="PENDING", nullable=True)
    event_date = Column(DateTime(timezone=True), nullable=True)
    details = Column(Text, nullable=True)
    budget_per_reservation =  Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),nullable=False)