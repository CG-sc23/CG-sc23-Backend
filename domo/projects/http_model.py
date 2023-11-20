from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[str] = None
    due_date: Optional[datetime] = None
    thumbnail_image: Optional[str] = None


class ModifyProjectRequest(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
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


class MakeProjectInviteRequest(BaseModel):
    project_id: int
    invitee_id: int
    role: str


class ReplyProjectInviteRequest(BaseModel):
    project_id: int
    inviter_id: int
    accept: bool
