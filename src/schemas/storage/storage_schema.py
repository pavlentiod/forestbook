from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path

from fastapi import UploadFile
from pydantic import BaseModel, HttpUrl

# logger = getLogger(__name__)


class FileOutput(BaseModel):
    """
    Represents the result of an upload operation
    Attributes:
        file (Bytes): File saved to memory
        path (Path | str): Path to file in local storage
        url (HttpUrl | str): A URL for accessing the object.
        size (int): Size of the file in bytes.
        filename (str): Name of the file.
        status (bool): True if the upload is successful else False.
        error (str): Error message for failed upload.
        message: Response Message
    """
    file: bytes = b''
    path: Path | str = ''
    url: HttpUrl | str = ''
    size: int = 0
    filename: str = ''
    content_type: str | None = ''
    status: bool = True
    error: str = ''
    message: str = ''


