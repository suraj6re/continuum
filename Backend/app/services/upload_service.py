import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.models.drawing import Drawing
from app.utils.file_identifier import identify_file_type, is_allowed_file

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 52428800))  # 50MB

async def save_upload_file(upload_file: UploadFile) -> Drawing:
    """Save uploaded file and create database record"""
    
    # Validate file extension
    if not is_allowed_file(upload_file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Generate unique filename
    file_ext = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Save file
    file_size = 0
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await upload_file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                os.remove(file_path)
                raise HTTPException(status_code=413, detail="File too large")
            await f.write(chunk)
    
    # Identify file type
    file_type = identify_file_type(file_path)
    
    # Create database record
    drawing = Drawing(
        filename=unique_filename,
        original_filename=upload_file.filename,
        file_type=file_type,
        file_size=file_size,
        file_path=file_path
    )
    await drawing.insert()
    
    return drawing
