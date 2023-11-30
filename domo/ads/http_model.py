from pydantic import BaseModel, EmailStr


class CreateAdRequest(BaseModel):
    company_email: EmailStr
    company_name: str
    requester_email: EmailStr
    requester_name: str
    ads_purpose: str
    ads_file_link: str


class GetAllAdsResponse(BaseModel):
    success: bool
    requests: list


class GetAdLinkResponse(BaseModel):
    success: bool
    file_link: str
