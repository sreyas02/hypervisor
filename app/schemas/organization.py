from pydantic import BaseModel
from typing import Optional, List
from app.schemas.user import User

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(OrganizationBase):
    pass

class OrganizationInDBBase(OrganizationBase):
    id: int
    invite_code: str

    class Config:
        from_attributes = True

class Organization(OrganizationInDBBase):
    users: List[User] = []

class OrganizationInDB(OrganizationInDBBase):
    pass 