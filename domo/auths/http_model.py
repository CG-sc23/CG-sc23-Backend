from typing import Optional

from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    github_link: Optional[str] = None
    short_description: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    success: bool
    token: str


class SocialSignInResponse(BaseModel):
    success: bool
    is_user: bool
    token: str


class SocialSignUpRequest(BaseModel):
    name: str
    pre_access_token: str
    github_link: Optional[str] = None
    short_description: Optional[str] = None


class SocialPreSignUpResponse(BaseModel):
    success: bool
    is_user: bool
    pre_access_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetCheckRequest(BaseModel):
    email: EmailStr
    token: str


class PasswordResetConfirmRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str


class EmailVerifyRequest(BaseModel):
    email: EmailStr


class EmailVerifyConfirmRequest(BaseModel):
    email: EmailStr
    token: str
