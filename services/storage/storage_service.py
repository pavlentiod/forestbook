import asyncio
import json
from abc import abstractmethod, ABC
from functools import cache
from io import BytesIO
from typing import List
from urllib.parse import urlencode

import boto3
from fastapi import UploadFile

from config import settings
from schemas.event.event_file_schema import EventFileOutput
from schemas.results.results_schema import Results
from schemas.storage.storage_schema import FileOutput


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

    async def __call__(self, file: UploadFile | None = None, files: list[UploadFile] | None = None) -> FileOutput | list[
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
    @property
    @cache
    def client(self):
        region_name = settings.aws.AWS_DEFAULT_REGION
        return boto3.client('s3', endpoint_url='https://storage.yandexcloud.net', region_name=region_name)


    async def upload(self, *, file: UploadFile) -> FileOutput:
        try:
            extra_args = self.config.get('extra_args', {})
            bucket = settings.aws.AWS_BUCKET_NAME
            await asyncio.to_thread(self.client.upload_fileobj, file.file, bucket, file.filename, ExtraArgs=extra_args)
            url = f"https://storage.yandexcloud.net/{bucket}/{urlencode(file.filename.encode('utf8'))}"
            file = FileOutput(url=url, message=f'{file.filename} uploaded successfully', filename=file.filename, content_type=file.content_type, size=file.size)
            return file
        except Exception as err:
            # print(err)
            return FileOutput(status=False, error=str(err), message='File upload was unsuccessful')


    async def upload_to_json(self, *, data: dict, filename: str) -> FileOutput:
        file = UploadFile(file=BytesIO(json.dumps(data, default=str).encode('UTF-8')), filename=filename)
        try:
            extra_args = self.config.get('extra_args', {})
            bucket = settings.aws.AWS_BUCKET_NAME
            await asyncio.to_thread(self.client.upload_fileobj, file.file, bucket, file.filename, ExtraArgs=extra_args)
            url = f"https://storage.yandexcloud.net/{bucket}/{urlencode(file.filename.encode('utf8'))}"
            file = FileOutput(url=url, message=f'{file.filename} uploaded successfully', filename=file.filename, content_type=file.content_type, size=file.size)
            return file
        except Exception as err:
            print(err)
            return FileOutput(status=False, error=str(err), message='File upload was unsuccessful')


    async def multi_upload(self, *, files: list[UploadFile]):
        tasks = [asyncio.create_task(self.upload(file=file)) for file in files]
        return await asyncio.gather(*tasks)

    async def download(self, key: str) -> bytes:
        try:
            bucket = settings.aws.AWS_BUCKET_NAME
            response = await asyncio.to_thread(self.client.get_object, Bucket=bucket, Key=key)
            return await asyncio.to_thread(response['Body'].read)
        except Exception as err:
            print(err)
            return b''


    async def download_json(self, key: str) -> bytes:
        try:
            bucket = settings.aws.AWS_BUCKET_NAME
            response = await asyncio.to_thread(self.client.get_object, Bucket=bucket, Key=key)
            body = await asyncio.to_thread(response['Body'].read)
            return json.loads(body)
        except Exception as err:
            print(err)
            return b''

    async def upload_results(self, results: Results, filenames: EventFileOutput):
        await self.upload_to_json(data=results.splits, filename=filenames.splits_path)
        await self.upload_to_json(data=results.routes, filename=filenames.routes_path)
        await self.upload_to_json(data=results.results, filename=filenames.results_path)