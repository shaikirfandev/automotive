"""Auth service schemas."""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class Role(str, Enum):
    USER = "user"
    MERCHANT = "merchant"
    ADMIN = "admin"


class RegisterRequest(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(default="", max_length=15)
    role: Role = Role.USER


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800
    user_id: str
    role: Role


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


class UserClaims(BaseModel):
    user_id: str
    email: str
    role: Role
    exp: int
