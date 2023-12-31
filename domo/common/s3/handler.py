import io
import logging
import os
import secrets

import boto3
from common.const import ReturnCode
from common.http_model import SimpleFailResponse
from django.http import JsonResponse
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
        except Exception as e:
            return ReturnCode.FAIL, e

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
        logging.error(profile_image_link)
        return JsonResponse(
            SimpleFailResponse(
                success=False, reason="Error uploading profile image."
            ).model_dump(),
            status=500,
        )
    return profile_image_link


class GeneralHandler:
    def __init__(self, type, user_email=None):
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
        self.user_email = user_email
        self.type = type
        if type == "resource":
            self.prefix = "resources"
        elif type == "profile":
            self.prefix = "users"

    def remove_resource(self, resource_link):
        if self.type == "resource":
            key = resource_link.split("/")[-1]
        elif self.type == "profile":
            key = resource_link.split("/")[-4:]
            key = "/".join(key)
        if not key:
            return False
        try:
            self.s3_client.delete_object(
                Bucket=self.aws_s3_bucket_name,
                Key=f"{self.prefix}/{key}",
            )
        except:
            return False
        return True

    def check_resource_links(self, resource_links):
        if self.type == "resource":
            if isinstance(resource_links, str):
                resource_links = [resource_links]
            for resource_link in resource_links:
                key = resource_link.split("/")[-1]
                try:
                    self.s3_client.head_object(
                        Bucket=self.aws_s3_bucket_name,
                        Key=f"{self.prefix}/{key}",
                    )
                except:
                    return False
        elif self.type == "profile":
            key = resource_links.split("/")[-4:]
            key = "/".join(key)
            try:
                self.s3_client.head_object(
                    Bucket=self.aws_s3_bucket_name,
                    Key=f"{self.prefix}/{key}",
                )
            except:
                return False

        else:
            return False

        return True

    @staticmethod
    def is_valid_object_type(object_type):
        return object_type in ["jpg", "jpeg", "png", "gif"]

    def create_presigned_url(self, object_name):
        object_type = object_name.split(".")[-1]

        if not self.is_valid_object_type(object_type):
            return ReturnCode.INVALID_ACCESS, None

        if self.type == "resource":
            random_token = secrets.token_urlsafe(16)
            key = f"{self.prefix}/{random_token}.{object_type}"
        elif self.type == "profile":
            key = f"{self.prefix}/{self.user_email}/profile/image/profile-image.{object_type}"
        else:
            return ReturnCode.INVALID_ACCESS, None
        try:
            response = self.s3_client.generate_presigned_post(
                Bucket=self.aws_s3_bucket_name,
                Key=key,
                ExpiresIn=600,
            )
        except Exception as e:
            return ReturnCode.FAILED_CREATE_PRESIGNED_URL, e

        return ReturnCode.SUCCESS, response


if __name__ == "__main__":
    test = GeneralHandler("resource")
    result = test.create_presigned_url("test.gif")
    print(result)
