from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True
