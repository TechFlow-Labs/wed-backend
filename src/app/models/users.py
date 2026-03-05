from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.db import Base

class User(Base):



    #Δημιουργεία User Table

    __tablename__ = "users"
    __table_args__ = {"schema": "weddingplan"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String(50), server_default=text("'COUPLE'"))
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, server_default=text("now()"))
