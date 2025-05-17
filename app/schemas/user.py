from pydantic import BaseModel, EmailStr
from typing import Optional
from app.db.models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    role: Optional[UserRole] = UserRole.DEVELOPER

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    organization_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str 