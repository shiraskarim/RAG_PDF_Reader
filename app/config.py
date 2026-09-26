import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
print("AWS_REGION:", AWS_REGION)
print("AWS_SECRET_ACCESS_KEY:", AWS_SECRET_ACCESS_KEY)
print("S3_BUCKET_NAME:", S3_BUCKET_NAME)
