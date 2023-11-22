from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ModifyUserInfoRequest(BaseModel):
    name: Optional[str] = None


class ModifyUserDetailInfoRequest(BaseModel):
    name: Optional[str] = None
    github_link: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    profile_image_link: Optional[str] = None


class GetUserInfoResponse(BaseModel):
    success: bool
    user_id: int
    email: str
    name: str
    profile_image_link: Optional[str] = None
    profile_image_updated_at: Optional[datetime] = None
    provider: str


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
    profile_image_updated_at: Optional[datetime] = None
    github_link: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    grade: Optional[int] = None
    like: Optional[int] = None
    rating: Optional[float] = None


class GetSearchResponse(BaseModel):
    success: bool
    result: list[dict]


class GetProjectInviteResponse(BaseModel):
    success: bool
    result: list[dict]
