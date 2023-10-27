from typing import Optional

from pydantic import BaseModel, EmailStr


class SimpleFailResponse(BaseModel):
    success: bool
    reason: str


class SimpleSuccessResponse(BaseModel):
    success: bool


class SignUpRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    provider: str
    github_link: Optional[str] = None
    short_description: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    success: bool
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetCheckRequest(BaseModel):
    email: EmailStr
    token: str


class PasswordResetConfirmRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str
