from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateTaskGroupRequest(BaseModel):
    title: str
    due_date: Optional[datetime] = None


class CreateTaskGroupResponse(BaseModel):
    success: bool
    task_group_id: int
    title: str
    status: str
    created_at: datetime
    due_date: Optional[datetime] = None


class ModifyTaskGroupRequest(BaseModel):
    title: str
    status: str
    due_date: Optional[datetime] = None


class GetTaskGroupResponse(BaseModel):
    success: bool
    task_group_id: int
    project: dict
    milestone: dict
    tasks: list
    created_by: dict
    title: str
    status: str
    created_at: datetime
    due_date: Optional[datetime] = None
    permission: str
