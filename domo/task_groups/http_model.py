from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateTaskGroupRequest(BaseModel):
    title: str


class CreateTaskGroupResponse(BaseModel):
    success: bool
    task_group_id: int
    title: str
    status: str
    created_at: datetime


class ModifyTaskGroupRequest(BaseModel):
    title: str
    status: str


class GetTaskGroupResponse(BaseModel):
    success: bool
    task_group_id: int
    project: dict
    milestone: dict
    created_by: dict
    title: str
    status: str
    created_at: datetime
    permission: str
