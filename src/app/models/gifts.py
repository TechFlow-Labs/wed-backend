from sqlalchemy import Column, String, DateTime, text, Boolean, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database.db import Base

class Gifts(Base):



   #Δημιουργία gifts Table

    __tablename__ = "gifts"
    __table_args__ = {"schema": "weddingplan"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("weddingplan.users.id"), nullable=False)
    item_name = Column(String(255), nullable=False)
    short_description = Column(String(255))
    long_description = Column(Text)
    category = Column(String(100))
    main_image_url = Column(Text)
    gallery_image_urls = Column(ARRAY(Text))
    created_at = Column(DateTime, server_default=text("now()"))
