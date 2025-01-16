import asyncio
from abc import abstractmethod, ABC
from functools import cache
from typing import List

import boto3
from fastapi import UploadFile

from src.config import settings
from src.schemas.storage.storage_schema import FileOutput
from src.services.redis_storage.redis_service import RedisStorage


class CloudUpload(ABC):
    """
    Methods:
        upload: Uploads a single object to the cloud
        multi_upload: Upload multiple objects to the cloud
    Attributes:
        config: A config dict
    """

    def __init__(self, config: dict | None = None):
        """
        Keyword Args:
            config (dict): A dictionary of config settings
        """
        self.config = config or {}

    async def __call__(self, file: UploadFile | None = None, files: list[UploadFile] | None = None) -> FileOutput | \
                                                                                                       list[
                                                                                                           FileOutput]:
        try:
            if file:
                return await self.upload(file=file)

            elif files:
                return await self.multi_upload(files=files)
            else:
                return FileOutput(status=False, error='No file or files provided', message='No file or files provided')
        except Exception as err:
            return FileOutput(status=False, error=str(err), message='File upload was unsuccessful')

    @abstractmethod
    async def upload(self, *, file: UploadFile) -> FileOutput:
        """"""

    @abstractmethod
    async def multi_upload(self, *, files: list[UploadFile]) -> list[FileOutput]:
        """"""


class StorageService(CloudUpload):
    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.redis_client = RedisStorage()
        self.redis_keys = settings.redis.storage

    @property
    @cache
    def client(self):
        region_name = settings.aws.AWS_DEFAULT_REGION
        return boto3.client('s3', endpoint_url='https://storage.yandexcloud.net', region_name=region_name)

    async def upload(self, *, file: UploadFile) -> FileOutput:
        try:
            extra_args = self.config.get('extra_args', {})
            bucket = settings.aws.AWS_BUCKET_NAME
            redis_key = self.redis_keys.key_by_filepath(file.filename)
            # Upload file to storage
            await asyncio.to_thread(self.client.upload_fileobj, file.file, bucket, file.filename, ExtraArgs=extra_args)

            # Clear existing cache and store new data
            self.redis_client.delete(redis_key)
            file_info = FileOutput(filename=file.filename, content_type=file.content_type, size=file.size)
            self.redis_client.set(redis_key, file)

            return file_info
        except Exception as err:
            return FileOutput(status=False, error=str(err), message='File upload was unsuccessful')

    async def download(self, key: str) -> bytes:
        redis_key = self.redis_keys.key_by_filepath(key)
        # Check cache before downloading
        if (cached_data := self.redis_client.get(redis_key)) is not None:
            return cached_data

        try:
            bucket = settings.aws.AWS_BUCKET_NAME
            response = await asyncio.to_thread(self.client.get_object, Bucket=bucket, Key=key)
            content = await asyncio.to_thread(response['Body'].read)

            # Cache the content
            self.redis_client.set(redis_key, content)
            return content
        except Exception:
            return b''

    async def delete(self, key: str) -> bool:
        redis_key = self.redis_keys.key_by_filepath(key)
        try:
            bucket = settings.aws.AWS_BUCKET_NAME

            # Delete from storage
            await asyncio.to_thread(self.client.delete_object, Bucket=bucket, Key=key)

            # Remove cache entry
            self.redis_client.delete(redis_key)
            return True
        except Exception:
            return False

    async def update(self, key: str, file: UploadFile) -> FileOutput:

        # Delete and upload new file
        await self.delete(key)
        return await self.upload(file=file)

    async def list_files(self, folder: str) -> List[str]:
        redis_key = self.redis_keys.key_by_filepath(folder)

        # Check cache before listing
        if (cached_files := self.redis_client.get(redis_key)) is not None:
            return cached_files

        try:
            bucket = settings.aws.AWS_BUCKET_NAME
            response = await asyncio.to_thread(self.client.list_objects_v2, Bucket=bucket, Prefix=folder)
            files = response.get('Contents', [])
            file_keys = [file['Key'] for file in files if 'Key' in file]

            # Cache the file list
            self.redis_client.set(redis_key, file_keys)
            return file_keys
        except Exception as err:
            raise RuntimeError(f"Failed to list files in folder {folder}: {str(err)}")

    async def multi_upload(self, *, files: list[UploadFile]) -> list[FileOutput]:
        for file in files:
            await self.upload(file=file)
        return True