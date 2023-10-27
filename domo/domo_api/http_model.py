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
    github_link: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    success: bool
    token: str


class SocialSignUpRequest(BaseModel):
    email: EmailStr
    name: str
    provider: str
    pre_access_token: str
    github_link: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None


class SocialSignUpResponse(BaseModel):
    success: bool
    email: EmailStr
    message: str
    pre_access_token: str
    provider: str
