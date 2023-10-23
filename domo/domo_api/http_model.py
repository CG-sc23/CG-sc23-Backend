from pydantic import BaseModel, EmailStr


class SimpleFailResponse(BaseModel):
    success: bool
    reason: str


class SimpleSuccessResponse(BaseModel):
    success: bool


class SignUpRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    github_link: str | None
    short_description: str | None
    description: str | None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class SignInResponse(BaseModel):
    success: bool
    token: str
