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


class GetGithubUpdateStatusResponse(BaseModel):
    success: bool
    status: str
    last_update: datetime


class GetAllUserStackResponse(BaseModel):
    success: bool
    count: int
    stacks: dict


class GetAllUserKeywordResponse(BaseModel):
    success: bool
    keywords: dict


class GetCommonStackResponse(BaseModel):
    success: bool
    id: str
    url: str


class ModifyUserInfoRequest(BaseModel):
    name: Optional[str] = None


class ModifyUserDetailInfoRequest(BaseModel):
    name: Optional[str] = None
    github_link: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None


class GetUserInfoResponse(BaseModel):
    success: bool
    user_id: int
    email: str
    name: str
    profile_image_link: Optional[str] = None


class GetUserDetailInfoResponse(BaseModel):
    success: bool
    github_link: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    grade: Optional[int] = None
    like: Optional[int] = None
    rating: Optional[float] = None
    provider: str


class GetUserPublicDetailInfoResponse(BaseModel):
    success: bool
    email: str
    name: str
    profile_image_link: Optional[str] = None
    github_link: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    grade: Optional[int] = None
    like: Optional[int] = None
    rating: Optional[float] = None


class CreateProjectRequest(BaseModel):
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[str] = None
    due_date: Optional[datetime] = None
    thumbnail_image: Optional[str] = None


class ModifyProjectRequest(BaseModel):
    title: str
    status: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[str] = None
    due_date: Optional[datetime] = None
    thumbnail_image: Optional[str] = None


class CreateProjectResponse(BaseModel):
    success: bool
    project_id: int
    status: str
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[str] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    thumbnail_image: Optional[str] = None


class GetProjectResponse(BaseModel):
    success: bool
    project_id: int
    owner: dict
    status: str
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[str] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    thumbnail_image: Optional[str] = None
    permission: str


class GetAllProjectResponse(BaseModel):
    success: bool
    count: int
    projects: list


class GetPreSignedUrlResponse(BaseModel):
    success: bool
    url: str
    aws_response: dict


class MakeProjectInviteRequest(BaseModel):
    project_id: int
    invitee_id: int
    role: str


class ReplyProjectInviteRequest(BaseModel):
    project_id: int
    inviter_id: int
    accept: bool
