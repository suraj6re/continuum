from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from app.services.upload_service import save_upload_file
from app.models.drawing import Drawing
from typing import List
import os

router = APIRouter(prefix="/api/upload", tags=["upload"])

@router.post("/drawing", response_model=dict)
async def upload_drawing(file: UploadFile = File(...)):
    """Upload a construction drawing file"""
    try:
        drawing = await save_upload_file(file)
        return {
            "success": True,
            "message": "File uploaded successfully",
            "data": {
                "id": str(drawing.id),
                "filename": drawing.filename,
                "original_filename": drawing.original_filename,
                "file_type": drawing.file_type,
                "file_size": drawing.file_size,
                "status": drawing.status,
                "uploaded_at": drawing.uploaded_at.isoformat()
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drawings", response_model=dict)
async def get_all_drawings():
    """Get all uploaded drawings"""
    drawings = await Drawing.find_all().to_list()
    return {
        "success": True,
        "data": [
            {
                "id": str(d.id),
                "filename": d.filename,
                "original_filename": d.original_filename,
                "file_type": d.file_type,
                "file_size": d.file_size,
                "status": d.status,
                "uploaded_at": d.uploaded_at.isoformat(),
                "processed": d.processed,
                "processed_at": d.processed_at.isoformat() if d.processed_at else None,
                "processing_error": d.processing_error,
                "entity_count": d.entity_count,
                "pipeline_type": d.pipeline_type
            }
            for d in drawings
        ]
    }

@router.get("/drawing/{drawing_id}", response_model=dict)
async def get_drawing(drawing_id: str):
    """Get specific drawing details"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    # Return complete drawing data as dict
    drawing_dict = drawing.dict()
    drawing_dict['id'] = str(drawing.id)
    drawing_dict['uploaded_at'] = drawing.uploaded_at.isoformat()
    if drawing.processed_at:
        drawing_dict['processed_at'] = drawing.processed_at.isoformat()
    
    return {
        "success": True,
        "data": drawing_dict
    }
