import boto3
import asyncio
from app.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
)


s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


def _upload_file(file_path: str, s3_key: str):

    s3_client.upload_file(
        file_path,
        S3_BUCKET_NAME,
        s3_key,
    )

    return f"s3://{S3_BUCKET_NAME}/{s3_key}"

async def upload_file(file_path: str, s3_key: str):

    return await asyncio.to_thread(
        _upload_file,
        file_path,
        s3_key
    )