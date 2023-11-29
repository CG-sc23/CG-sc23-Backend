from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateReportRequest(BaseModel):
    title: str
    description: Optional[str] = None


class GetAllReportResponse(BaseModel):
    success: bool
    count: int
    reports: list[dict]
