from datetime import datetime
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


class GithubAccountCheckRequest(BaseModel):
    github_link: str


class ModifyUserInfoRequest(BaseModel):
    name: Optional[str] = None
    github_link: Optional[str] = None
    short_description: Optional[str] = None
    is_public: Optional[bool] = None


class GetUserInfoResponse(BaseModel):
    success: bool
    email: str
    name: str
    has_profile_image: bool
    is_public: bool
    github_link: Optional[str] = None
    short_description: Optional[str] = None
    grade: Optional[int] = None
    like: Optional[int] = None
    rating: Optional[float] = None
    provider: str
    last_login: datetime
