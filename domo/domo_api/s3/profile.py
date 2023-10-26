import os

import boto3


class ProfileHandler:
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
        self.s3_resource = self.s3_session.resource("s3")

    def upload_image(self, user_email, file):
        s3 = self.s3_client
        file_name = f"users/{user_email}/profile-image.jpeg"

        try:
            s3.upload_fileobj(file, self.aws_s3_bucket_name, file_name)
            return True
        except:
            self.delete_directory(user_email)
            return False

    def delete_directory(self, user_email):
        s3 = self.s3_resource

        bucket = s3.Bucket(self.aws_s3_bucket_name)

        for obj in bucket.objects.filter(Prefix=f"users/{user_email}/"):
            obj.delete()


if __name__ == "__main__":
    profile_handler = ProfileHandler()
    profile_handler.delete_directory("test123@test.io")
