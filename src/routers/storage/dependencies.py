from fastapi import UploadFile, File, HTTPException

from src.services.storage.storage_service import StorageService


async def get_storage_service() -> StorageService:
    """
    Dependency to provide an instance of StorageService.
    """
    return StorageService()


def validate_image_files(files: list[UploadFile] = File(...)):
    """
    Dependency to validate that all uploaded files are either JPG or PNG.
    Raises an HTTPException if any file is not in the allowed formats.
    """
    allowed_extensions = {"jpg", "jpeg", "png"}
    for file in files:
        # Extract the file extension
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format: {file.filename}. Allowed formats: jpg, jpeg, png."
            )
    return files
