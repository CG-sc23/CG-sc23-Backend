import os
import secrets

import boto3
from domo_api.const import ReturnCode


class Handler:
    def __init__(self):
        self.aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")

        # # For Local Test
        # self.s3_session = boto3.Session(profile_name="minio")
        # self.s3_client = self.s3_session.client(
        #     "s3", endpoint_url="http://127.0.0.1:9000"
        # )
        # self.s3_resource = self.s3_session.resource(
        #     "s3", endpoint_url="http://127.0.0.1:9000"
        # )
        self.s3_client = boto3.client("s3")
        self.s3_resource = boto3.resource("s3")

    def upload_image(self, user_email, path, file):
        s3 = self.s3_client
        available_paths = [
            "profile/image",
            "profile/description",
        ]
        full_path = f"users/{user_email}/{path}" if path in available_paths else None
        if not full_path:
            return ReturnCode.INVALID_ACCESS, None

        random_token = secrets.token_urlsafe(16)
        uploaded_file_link = (
            f"https://{self.aws_s3_bucket_name}.s3.ap-northeast-2."
            f"amazonaws.com/{full_path}/{random_token}/image.png"
        )
        full_path += f"/{random_token}/image.png"

        try:
            s3.upload_fileobj(file, self.aws_s3_bucket_name, full_path)
            return ReturnCode.SUCCESS, uploaded_file_link
        except:
            return ReturnCode.FAIL, None
