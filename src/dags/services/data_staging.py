import os
from io import IOBase
from typing import BinaryIO
from urllib.parse import urlparse

import boto3

from services.data_retriever import DataRetriever as DataDownloader
from services.logger import Logger


class DataStagingService:
    """
    Handles dataset staging into S3 based on its dataLocation.
    Supports 'http' kind (streaming-safe).
    """

    def __init__(self):
# def __init__(self, aws_region: str, s3_bucket: str = None):
        """
        Initialize the file storage service.

        :param s3_bucket: Name of the S3 bucket to store files in.
        :param aws_region: AWS region (default: us-east-1).
        """
        # self.s3_bucket = s3_bucket
        # if s3_bucket:
        #     self.s3_client = boto3.client("s3", region_name=aws_region)
        # else:
        #     self.s3_client = None

    def store(self, stream: IOBase, destination_path: str) -> str:
        """
        Stores a binary file stream to a local file path.

        :param stream: A binary file-like object (e.g., io.BytesIO, open(file, 'rb')).
        :param destination_path: Destination file path.
        :return: The full path where the file was stored.
        """
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(destination_path, "wb") as f:
            f.write(stream.read())
        return os.path.abspath(destination_path)

    # def store_to_s3(self, stream: BinaryIO, s3_key: str) -> str:
    #     """
    #     Stores a binary file stream to an S3 path.
    #
    #     :param stream: A binary file-like object (e.g., io.BytesIO, open(file, 'rb')).
    #     :param s3_key: The S3 object key (path inside the bucket).
    #     :return: The S3 URI of the uploaded file.
    #     """
    #     if not self.s3_client or not self.s3_bucket:
    #         raise RuntimeError("S3 client not configured. Provide an S3 bucket during initialization.")
    #
    #     try:
    #         self.s3_client.upload_fileobj(stream, self.s3_bucket, s3_key)
    #         return f"s3://{self.s3_bucket}/{s3_key}"
    #     except (BotoCoreError, NoCredentialsError) as e:
    #         raise RuntimeError(f"Failed to upload to S3: {e}")