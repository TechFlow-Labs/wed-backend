from sqlalchemy import Column, String, DateTime, text, Boolean, ForeignKey, Text, Numeric # Πρόσθεσα το Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.db import Base

class Budget(Base):


    #Δημιουργεία Budget Table



    __tablename__ = "budgets"
    __table_args__ = {"schema": "weddingplan"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("weddingplan.users.id"),nullable=False, unique=True)
    total_budget = Column(Numeric(12, 2), default=0.00)
    updated_at = Column(DateTime, server_default=text("now()"), onupdate=text("now()"))
