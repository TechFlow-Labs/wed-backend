from pydantic import BaseModel, EmailStr, ConfigDict
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

class UserProfileResponseSchema(BaseModel):
    # Base User Fields
    id: UUID
    role: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Partner Profile Fields (Optional, so Couples don't break the schema)
    business_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdateSchema(BaseModel):
    # Base User Fields
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Partner Profile Fields
    business_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None