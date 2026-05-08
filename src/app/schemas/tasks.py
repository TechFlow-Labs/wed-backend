from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional

class TaskDashboard(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    notes: Optional[str]
    is_completed: bool
    due_date: Optional[datetime]

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    notes: Optional[str] = None
    is_completed: bool = False
    due_date: Optional[datetime] = None

class UpdateTask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    is_completed: Optional[bool] = False
    due_date: Optional[datetime] = None
