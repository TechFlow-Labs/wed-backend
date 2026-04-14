from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class BlogCreateSchema(BaseModel):
    title: str
    content: str
    excerpt: Optional[str] = None
    is_published: bool = False


class BlogUpdateSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    is_published: Optional[bool] = None


class BlogResponseSchema(BaseModel):
    id: UUID
    author_id: UUID
    title: str
    content: str
    excerpt: Optional[str] = None
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlogPublicSchema(BaseModel):
    id: UUID
    title: str
    content: str
    excerpt: Optional[str] = None
    author_name: str
    created_at: datetime
    updated_at: datetime
