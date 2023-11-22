from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateMilestoneRequest(BaseModel):
    subject: str
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None


class CreateMilestoneResponse(BaseModel):
    success: bool
    id: int
    subject: str
    tags: Optional[list[str]] = None
    status: str
    created_at: datetime
    due_date: Optional[datetime] = None


class ModifyMilestoneRequest(BaseModel):
    subject: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[list[str]] = None
    due_date: Optional[datetime] = None


class GetMilestoneResponse(BaseModel):
    success: bool
    id: int
    project: dict
    created_by: dict
    subject: str
    tags: Optional[list[str]] = None
    status: str
    created_at: datetime
    due_date: Optional[datetime] = None
    task_groups: list
    permission: str
