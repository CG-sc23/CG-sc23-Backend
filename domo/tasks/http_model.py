from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    is_public: bool


class ModifyTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    is_public: Optional[bool] = None


class CreateTaskResponse(BaseModel):
    success: bool
    id: int
    title: str
    description: Optional[str] = None
    description_resource_links: Optional[list[str]] = None
    created_at: datetime
    tags: Optional[list[str]] = None
    is_public: bool


class GetTaskResponse(BaseModel):
    success: bool
    id: int
    project: dict
    milestone: dict
    task_group: dict
    owner: dict
    title: str
    description: Optional[str] = None
    description_resource_links: Optional[str] = None
    created_at: datetime
    tags: Optional[list[str]] = None
    members: list
    is_public: bool
    permission: str


class GetTaskAllResponse(BaseModel):
    success: bool
    total_count: int
    tasks: list
