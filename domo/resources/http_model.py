from pydantic import BaseModel


class GetPreSignedUrlResponse(BaseModel):
    success: bool
    url: str
    aws_response: dict
