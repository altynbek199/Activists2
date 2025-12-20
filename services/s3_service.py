import mimetypes
from aiobotocore.session import get_session
from contextlib import asynccontextmanager
from botocore.config import Config
import certifi
from fastapi import UploadFile
import datetime
from settings import settings

class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
            static_domain: str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url
        }
        self.bucket_name = bucket_name
        self.static_domain = static_domain
        self.session = get_session()

        self.s3_config = Config(
            signature_version="s3v4",
            s3={'addressing_style': "path"}
        )

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", config=self.s3_config, verify=certifi.where(), **self.config) as client:
            yield client   

    async def get_file(self, s3_key: str) -> bytes:
        async with self.get_client() as client:
            response = await client.get_object(
                 Bucket=self.bucket_name,
                 Key=s3_key,
            )
            async with response["Body"] as stream:
                 return await stream.read()    

    async def upload_file(
            self,
            filename: str,
            file: bytes,
    ) -> str:
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        extension = filename.split(".")[-1]
        name = filename.split(".")[0]
        unique_filename = f"{name}-{timestamp}.{extension}"

        content_type, _ = mimetypes.guess_type(filename)
        
        async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=unique_filename,
                    Body=file,
                    ContentType=content_type,
                    ACL="public-read"
                )
        return f'https://{self.static_domain}/{unique_filename}' 

    async def delete_file(self, s3_key: str):
         async with self.get_client() as client:
             await client.delete_object(
                  Bucket=self.bucket_name,
                  Key=s3_key,
             )  
s3_client = S3Client(
    access_key=settings.ACCESS_KEY,
    secret_key=settings.SECRET_KEY,
    endpoint_url=settings.ENDPOINT_URL,
    bucket_name=settings.BUCKET_NAME,
    static_domain=settings.STATIC_DOMAIN,
)

