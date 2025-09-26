from pydantic import BaseModel, EmailStr
from typing import Optional, Literal

class UserBase(BaseModel):
    username: str
    email: str
    role: Literal["admin", "leitor"] = "leitor"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None