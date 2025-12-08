from pydantic import BaseModel, EmailStr
from typing import Optional


class AdminCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    is_superuser: Optional[bool] = False


class AdminResponse(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
