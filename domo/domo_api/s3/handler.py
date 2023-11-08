import io
import os
import secrets

import boto3
from botocore.exceptions import ClientError
from django.http import JsonResponse
from domo_api.const import ReturnCode
from domo_api.http_model import SimpleFailResponse
from PIL import Image


class ProfileImageUploader:
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

    def upload_image(self, user_email, path, image_file):
        s3 = self.s3_client
        available_paths = [
            "profile/image",
            "profile/description",
        ]
        full_path = f"users/{user_email}/{path}" if path in available_paths else None
        if not full_path:
            return ReturnCode.INVALID_ACCESS, None

        random_token = secrets.token_urlsafe(16)

        if path == "profile/image":
            uploaded_file_link = (
                f"https://{self.aws_s3_bucket_name}.s3.ap-northeast-2."
                f"amazonaws.com/{full_path}/profile-image.jpeg"
            )
            full_path += f"/profile-image.jpeg"
        else:
            uploaded_file_link = (
                f"https://{self.aws_s3_bucket_name}.s3.ap-northeast-2."
                f"amazonaws.com/{full_path}/{random_token}/image.jpeg"
            )
            full_path += f"/{random_token}/image.jpeg"

        image_file = self._convert_image_to_jpeg(image_file)
        try:
            s3.upload_fileobj(
                image_file,
                self.aws_s3_bucket_name,
                full_path,
                ExtraArgs={"ContentType": "image/jpeg"},
            )
            return ReturnCode.SUCCESS, uploaded_file_link
        except:
            return ReturnCode.FAIL, None

    @staticmethod
    def _convert_image_to_jpeg(image_file):
        image = Image.open(image_file)
        output_image_io = io.BytesIO()
        image.convert("RGB").save(output_image_io, format="JPEG", quality=90)
        converted_image_file = io.BytesIO(output_image_io.getvalue())
        return converted_image_file


def upload_profile_image(request_data, profile_image):
    profile_handler = ProfileImageUploader()
    profile_upload_success, profile_image_link = profile_handler.upload_image(
        request_data.email, "profile/image", profile_image
    )

    if profile_upload_success == ReturnCode.INVALID_ACCESS:
        return JsonResponse(
            SimpleFailResponse(success=False, reason="Invalid request.").model_dump(),
            status=400,
        )
    if profile_upload_success == ReturnCode.FAIL:
        return JsonResponse(
            SimpleFailResponse(
                success=False, reason="Error uploading profile image."
            ).model_dump(),
            status=500,
        )
    return profile_image_link


class GeneralHandler:
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
        self.prefix = "resources"

    def remove_resource(self, resource_link):
        key = resource_link.split("/")[-1]
        try:
            self.s3_client.delete_object(
                Bucket=self.aws_s3_bucket_name,
                Key=f"{self.prefix}/{key}",
            )
        except:
            return False
        return True

    def check_resource_links(self, resource_links):
        for resource_link in resource_links:
            key = resource_link.split("/")[-1]
            try:
                self.s3_client.head_object(
                    Bucket=self.aws_s3_bucket_name,
                    Key=f"{self.prefix}/{key}",
                )
            except:
                return False
        return True

    @staticmethod
    def is_valid_object_type(object_type):
        return object_type in ["jpg", "jpeg", "png", "gif", "mp4"]

    def create_presigned_url(self, object_name):
        object_type = object_name.split(".")[-1]

        if not self.is_valid_object_type(object_type):
            return ReturnCode.INVALID_ACCESS, None

        random_token = secrets.token_urlsafe(16)
        key = f"{self.prefix}/{random_token}.{object_type}"
        try:
            response = self.s3_client.generate_presigned_post(
                Bucket=self.aws_s3_bucket_name,
                Key=key,
                ExpiresIn=600,
            )
        except:
            return ReturnCode.FAILED_CREATE_PRESIGNED_URL, None

        return ReturnCode.SUCCESS, response


if __name__ == "__main__":
    test = GeneralHandler()
    result = test.create_presigned_url("test.gif")
    print(result)
