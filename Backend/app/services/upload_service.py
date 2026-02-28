import os
import uuid
import aiofiles
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile, HTTPException
from app.models.drawing import Drawing
from app.utils.file_identifier import identify_file_type, is_allowed_file
from app.ai.pipeline import route_preprocessing
from app.ai.layer2_pipeline import run_layer2_pipeline

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
        file_path=file_path,
        status="processing"
    )
    await drawing.insert()
    
    # Process with Layer 1 pipeline
    try:
        result = route_preprocessing(file_path, file_type)
        
        # Store Layer 1 results in database
        drawing.processed = True
        drawing.processed_at = datetime.utcnow()
        drawing.status = "processed"
        drawing.geometry = result.get('geometry')
        drawing.bounding_box = result.get('bounding_box')
        drawing.text = result.get('text')
        drawing.scale_candidates = result.get('scale_candidates', [])
        drawing.units = result.get('units')
        drawing.layers = result.get('layers')
        drawing.blocks = result.get('blocks')
        drawing.pipeline_type = result.get('pipeline_type')
        drawing.entity_count = result.get('entity_count')
        drawing.intermediate_json = result.get('intermediate_json')
        
        # Run Layer 2 pipeline if vector
        if result.get('pipeline_type') == 'vector':
            try:
                layer2_result = run_layer2_pipeline(result)
                drawing.layer2_processed = True
                drawing.layer2_data = layer2_result
            except Exception as e:
                print(f"Layer 2 processing failed: {e}")
                drawing.layer2_processed = False
        
        await drawing.save()
        
    except Exception as e:
        # Store error but don't fail upload
        drawing.processed = False
        drawing.processing_error = str(e)
        drawing.status = "error"
        await drawing.save()
    
    return drawing
