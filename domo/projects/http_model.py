from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class CreateProjectRequest(BaseModel):
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    thumbnail_image: Optional[str] = None


class ModifyProjectRequest(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    due_date: Optional[datetime] = None
    thumbnail_image: Optional[str] = None


class CreateProjectResponse(BaseModel):
    success: bool
    id: int
    status: str
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    thumbnail_image: Optional[str] = None


class GetProjectResponse(BaseModel):
    success: bool
    id: int
    owner: dict
    status: str
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    created_at: datetime
    due_date: Optional[datetime] = None
    thumbnail_image: Optional[str] = None
    milestones: Optional[list] = None
    members: list
    permission: str


class GetProjectAllResponse(BaseModel):
    success: bool
    count: int
    projects: list


class GetAllProjectResponse(BaseModel):
    success: bool
    count: int
    projects: list


class MakeProjectInviteRequest(BaseModel):
    project_id: int
    invitee_emails: list[EmailStr]


class MakeProjectInviteDetailResponse(BaseModel):
    invitee_email: EmailStr
    success: bool
    reason: Optional[str] = None

    @classmethod
    def create(cls, invitee_email: str, success: bool, reason: str = None):
        return cls(invitee_email=invitee_email, success=success, reason=reason)


class MakeProjectInviteResponse(BaseModel):
    result: list[MakeProjectInviteDetailResponse]


class ChangeRoleRequest(BaseModel):
    user_email: EmailStr
    role: str


class KickMemberRequest(BaseModel):
    user_email: EmailStr


class GetJoinResponse(BaseModel):
    success: bool
    result: list


class ReplyJoinRequestModel(BaseModel):
    join_request_id: int
    accept: bool
