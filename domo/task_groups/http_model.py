from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateTaskGroupRequest(BaseModel):
    title: str
    due_date: Optional[datetime] = None


class CreateTaskGroupResponse(BaseModel):
    success: bool
    id: int
    title: str
    status: str
    created_at: datetime
    due_date: Optional[datetime] = None


class ModifyTaskGroupRequest(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None


class GetTaskGroupResponse(BaseModel):
    success: bool
    id: int
    project: dict
    milestone: dict
    tasks: list
    created_by: dict
    title: str
    status: str
    created_at: datetime
    due_date: Optional[datetime] = None
    permission: str
