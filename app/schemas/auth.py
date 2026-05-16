from pydantic import BaseModel, EmailStr
from .user import UserBase

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    status: str
    token: str
    message: str
    user: UserBase
