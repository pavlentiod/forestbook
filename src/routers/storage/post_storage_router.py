import pathlib
import uuid
from typing import List

from fastapi import APIRouter, Security, UploadFile, Depends, Response

from src.config import settings
from src.routers.storage.dependencies import get_storage_service, validate_image_files
from src.schemas.storage.storage_schema import FileListResponse, UploadResponse
from src.services.auth.dependencies import get_current_active_user
from src.services.storage.storage_service import StorageService

router = APIRouter()
endpoints = settings.api.storage


@router.delete(
    endpoints.delete.path,
    response_model=bool,
    dependencies=[Security(get_current_active_user, scopes=endpoints.delete.security)]
)
async def delete(
        _id: str,
        key: str,
        storage_service: StorageService = Depends(get_storage_service),
):
    """
    Delete a file from storage by its key.

    Args:
        _id (str): Unique identifier of the resource (e.g., user or post).
        key (str): Key of the file to be deleted in the storage.
        storage_service (StorageService): Service for handling storage operations.

    Returns:
        bool: True if the file was successfully deleted, False otherwise.
    """
    return await storage_service.delete(key=f"{settings.aws.tree.post_folder(_id)}{key}")


@router.get(
    endpoints.get_all.path,
    response_model=FileListResponse,
    dependencies=[Security(get_current_active_user, scopes=endpoints.get_all.security)]
)
async def get_all(
        _id: str,
        storage_service: StorageService = Depends(get_storage_service),
):
    """
    Retrieve a list of all files associated with the given ID.

    Args:
        _id (str): Unique identifier of the resource (e.g., user or post).
        storage_service (StorageService): Service for handling storage operations.

    Returns:
        FileListResponse: A list of file names in the storage folder.
    """
    file_names = await storage_service.list_files(f"{settings.aws.tree.post_folder(_id)}")
    return FileListResponse(files=[pathlib.Path(path).name for path in file_names])


@router.post(
    endpoints.upload.path,
    response_model=UploadResponse,
    dependencies=[Security(get_current_active_user, scopes=endpoints.upload.security)]
)
async def upload(
        _id: str,
        files: List[UploadFile] = Depends(validate_image_files),
        storage_service: StorageService = Depends(get_storage_service),
):
    """
    Upload a list of image files to storage.

    Args:
        _id (str): Unique identifier of the resource (e.g., user or post).
        files (List[UploadFile]): List of image files to upload, validated by `validate_image_files`.
        storage_service (StorageService): Service for handling storage operations.

    Returns:
        UploadResponse: A list of successfully uploaded file keys.
    """
    uploaded_files = []
    for file in files:
        ext = pathlib.Path(file.filename).suffix
        file.filename = f"{settings.aws.tree.post_folder(_id)}{str(uuid.uuid4())[:5]}{ext}"
        uploaded_files.append(file.filename)
    await storage_service.multi_upload(files=files)
    return UploadResponse(uploaded=uploaded_files)


@router.get(
    endpoints.download.path,
    dependencies=[Security(get_current_active_user, scopes=endpoints.download.security)]
)
async def download(
        _id: str,
        key: str,
        storage_service: StorageService = Depends(get_storage_service),
):
    """
    Download a file from storage by its key.

    Args:
        _id (str): Unique identifier of the resource (e.g., user or post).
        key (str): Key of the file to download from the storage.
        storage_service (StorageService): Service for handling storage operations.

    Returns:
        Response: File content with appropriate media type (e.g., image/png).
    """
    file_data = await storage_service.download(f"{settings.aws.tree.post_folder(_id)}{key}")
    return Response(file_data, media_type="image/png")
