from pathlib import Path
from typing import List

from pydantic import BaseModel, HttpUrl


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
    path: Path | str = ''
    size: int = 0
    filename: str = ''
    content_type: str | None = ''
    status: bool = True
    error: str = ''


class FileListResponse(BaseModel):
    files: List[str]


class UploadResponse(BaseModel):
    uploaded: List[str]
