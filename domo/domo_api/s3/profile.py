import os

import boto3


class ProfileHandler:
    def __init__(self):
        self.aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.aws_s3_bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")
        self.region_name = os.environ.get("AWS_REGION_NAME")

        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
        )
        self.s3_resource = boto3.resource(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name,
        )

    def upload_image(self, user_email, file):
        s3 = self.s3_client
        file_name = f"{user_email}/profile-image.jpeg"

        try:
            s3.upload_fileobj(file, self.aws_s3_bucket_name, file_name)
            return True
        except:
            self.delete_directory(user_email)
            return False

    def delete_directory(self, user_email):
        s3 = self.s3_resource

        bucket = s3.Bucket(self.aws_s3_bucket_name)

        for obj in bucket.objects.filter(Prefix=f"{user_email}/"):
            obj.delete()


if __name__ == "__main__":
    profile_handler = ProfileHandler()
    profile_handler.delete_directory("test123@test.io")
