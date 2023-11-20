from datetime import datetime

from pydantic import BaseModel


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
