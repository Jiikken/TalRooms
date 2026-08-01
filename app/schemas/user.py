from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    access_lvl: int = None
    last_login: datetime = None
    created: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
