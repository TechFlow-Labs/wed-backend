from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import List, Optional
from decimal import Decimal


# Δεδομένα τα οποία στέλνει ο χρήστης
class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    role: Optional[str] = "COUPLE"

# Απάντηση που επιστρέφουμε εμεις
class UserRegisterResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    created_at: datetime

# Τι στέλνει ο χρήστης για το Login
class UserLoginRequest(BaseModel):
    username: str
    password: str

# Απάντηση που επιστρέφουμε εμεις έπειτα απο το Login
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    role: str


class UserDashboard(BaseModel):
    id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    role: str
    class Config:
        from_attributes = True



class TaskDashboard(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    notes: Optional[str]
    is_completed: bool
    due_date: Optional[datetime]

    class Config:
        from_attributes = True

class GiftDashboard(BaseModel):
    id: UUID
    item_name: str
    category: Optional[str]
    short_description: Optional[str]
    long_description: Optional[str]
    main_image_url: Optional[str]
    gallery_image_urls: List[str]

    class Config:
        from_attributes = True



class BudgetDashboard(BaseModel):
    total_budget: float
    updated_at: datetime

    class Config:
        from_attributes = True

class GuestDashboard(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: Optional[str]
    phone_number: Optional[str]
    reservation_id: Optional[UUID] = None
    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    user: UserDashboard
    budget: BudgetDashboard
    tasks: List[TaskDashboard]
    gifts: List[GiftDashboard]
    guests: List[GuestDashboard]




# RESPONE SCHEMAS FOR TASKS, GIFTS, GUESTS, BUDGET



class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    notes: Optional[str] = None
    is_completed: bool = False
    due_date: Optional[datetime] = None



class GiftCreate(BaseModel):
    item_name: str
    category: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    main_image_url: Optional[str] = None
    gallery_image_urls: List[str] = []



class GuestCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    reservation_id: Optional[UUID] = None



class BudgetUpdate(BaseModel):
    total_budget: float



class UpdateTask(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    is_completed: Optional[bool] = False
    due_date: Optional[datetime] = None

