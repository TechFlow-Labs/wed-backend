from sqlalchemy import Column, String, DateTime, text, Boolean, ForeignKey, Text 
from sqlalchemy.dialects.postgresql import UUID 
import uuid
from database.db import Base 

class Tasks(Base):


    #Δημιουργια tasks Table

    __tablename__ = "tasks"
    __table_args__ = {"schema": "weddingplan"} 

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    user_id = Column(UUID(as_uuid=True), ForeignKey("weddingplan.users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text) 
    notes = Column(Text) 
    is_completed = Column(Boolean, default=False)
    due_date = Column(DateTime)
    created_at = Column(DateTime, server_default=text("now()"))