from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserBase(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    status: str
    token: str
    message: str
    user: UserBase
