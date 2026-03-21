from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional

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
