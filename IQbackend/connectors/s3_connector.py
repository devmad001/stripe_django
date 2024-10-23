import io
import uuid
import json
import boto3
import urllib
from django.conf import settings
from botocore.client import Config

class S3Connector:
    def __init__(self):
        self.s3 = boto3.resource(
            "s3",
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_ACCESS_KEY_SECRET,
            config=Config(signature_version="s3v4"),
        )

    def upload_file(self, file_path: str, file_content: io.BufferedReader):
        """
        Uploads a file to the S3 bucket

        :param file_path: Destination path in the S3 bucket. Example: 'sample/file.txt' will upload the file.txt to a folder sample
        :param file_content: The content of the file
        :return: The response from the S3 bucket

        :raises: Exception if the file cannot be uploaded
        """

        return self.s3.Bucket(settings.S3_BUCKET_NAME).put_object(Key=file_path, Body=file_content)

    def generate_presigned_get_url(self, file_path, expires_in_seconds: int = None, metadata: dict = None):
        """
        Generates a presigned URL for retrieving a file in the S3 bucket

        Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_url.html

        :param request: The request object
        :param metadata: Additional metadata to send with S3 request
        :return: The presigned URL

        :raises: Exception if the URL cannot be generated
        """

        params = {
            "Bucket": settings.S3_BUCKET_NAME,
        }

        if metadata:
            params["Metadata"] = metadata

        if expires_in_seconds is None:
            expires_in_seconds = 60

        if not file_path:
            raise Exception("File path is required for downloading a file")
        params["Key"] = file_path
        file_name = file_path.split("/")[-1]

        # Unicodes and special characters can cause issues for the Response-Content-Disposition header
        # Encode file name to avoid such issues
        encoded_file_name = urllib.parse.quote(file_name)
        params["ResponseContentDisposition"] = f"attachment; filename={encoded_file_name}"

        return (
            self.s3.meta.client.generate_presigned_url(
                ClientMethod='get_object',
                Params=params,
                ExpiresIn=expires_in_seconds)
        )

    def generate_presigned_post_url(self, request, expires_in_seconds: int = None, fields: dict = None, conditions: list = None):
        """
        Generates a presigned post URL for uploading a file in the S3 bucket

        Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/generate_presigned_post.html
        For more info on conditions, see:
        https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTConstructPolicy.html,
        https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-post-example.html


        :param request: The request object
        :param expires_in_seconds: The expiration time of the URL
        :param fields: The fields to send with the S3 request
        :param conditions: The conditions to enforce on the S3 request
        :return: The presigned URL

        :raises: Exception if the URL cannot be generated
        """

        data = json.loads(request.body)

        if not data:
            raise Exception("Request body is empty")

        if expires_in_seconds is None:
            expires_in_seconds = 120

        # Default max file size is 16MB
        default_max_file_size_bytes = 16000000

        # Set default conditions if not provided. Refer to the links above for more info
        if conditions is None:
            conditions = [
                {"bucket": S3_BUCKET_NAME},
                ["content-length-range", 0, default_max_file_size_bytes],
            ]

        file_name: str = data.get("file_name")
        if not file_name:
            raise Exception("File name is required for uploading a file")

        if file_name.find("/") != -1:
            raise Exception("File name cannot contain '/'")

        user_id = request.user.id
        file_path = f"{user_id}/{uuid.uuid4()}/{file_name}"

        # Key condition needs to set explicitly in case of presigned post
        conditions.append({"key": file_path})

        return (
            self.s3.meta.client.generate_presigned_post(
                Bucket=settings.S3_BUCKET_NAME,
                Key=file_path,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=expires_in_seconds
            )
        )