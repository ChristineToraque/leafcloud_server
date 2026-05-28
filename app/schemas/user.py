from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool = False

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_admin: bool = False

    class Config:
        from_attributes = True
