import os
import aiofiles
from fastapi import UploadFile
from core.config import settings

async def store_file(file: UploadFile, file_id: str) -> str:
    """
    Store uploaded file and return file path
    """
    # Create uploads directory if not exists
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    
    # Get file extension
    file_ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(upload_dir, f"{file_id}{file_ext}")
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return file_path 