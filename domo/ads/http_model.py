from pydantic import BaseModel, EmailStr


class CreateAdRequest(BaseModel):
    company_email: EmailStr
    company_name: str
    requester_email: EmailStr
    requester_name: str
    ads_purpose: str
    ads_file_link: str


class GetAdLinkResponse(BaseModel):
    success: bool
    site_link: str
    file_link: str
