from sqlalchemy import Column, String, DateTime, text, Boolean, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.db import Base


class Guests(Base):

    #Δημιουργεία Guests Table
    __tablename__ = "guests"
    __table_args__ = {"schema": "weddingplan"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("weddingplan.users.id"), nullable=False)
    reservation_id = Column(UUID(as_uuid=True), ForeignKey("weddingplan.reservations.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=text("now()"))
