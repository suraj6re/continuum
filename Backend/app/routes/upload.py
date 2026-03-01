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

@router.get("/drawing/{drawing_id}/layer2", response_model=dict)
async def get_layer2_data(drawing_id: str):
    """Get Layer 2 semantic analysis data"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    if not drawing.layer2_processed:
        raise HTTPException(status_code=404, detail="Layer 2 data not available")
    
    return {
        "success": True,
        "data": drawing.layer2_data
    }

@router.get("/drawing/{drawing_id}/layer3", response_model=dict)
async def get_layer3_data(drawing_id: str):
    """Get Layer 3 quantity takeoff data"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    if not drawing.layer3_processed:
        raise HTTPException(status_code=404, detail="Layer 3 data not available")
    
    return {
        "success": True,
        "data": drawing.layer3_data
    }

@router.get("/drawing/{drawing_id}/layer4", response_model=dict)
async def get_layer4_data(drawing_id: str):
    """Get Layer 4 QTO data"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    if not drawing.layer4_processed:
        raise HTTPException(status_code=404, detail="Layer 4 data not available")
    
    return {
        "success": True,
        "data": drawing.layer4_data
    }

@router.get("/drawing/{drawing_id}/layer5", response_model=dict)
async def get_layer5_data(drawing_id: str):
    """Get Layer 5 canonical model data"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    if not drawing.layer5_processed:
        raise HTTPException(status_code=404, detail="Layer 5 data not available")
    
    return {
        "success": True,
        "data": drawing.layer5_data
    }

@router.get("/drawing/{drawing_id}/layer6", response_model=dict)
async def get_layer6_data(drawing_id: str):
    """Get Layer 6 validation and confidence data"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    if not drawing.layer6_processed:
        raise HTTPException(status_code=404, detail="Layer 6 data not available")
    
    return {
        "success": True,
        "data": drawing.layer6_data
    }

@router.get("/drawing/{drawing_id}/layer7", response_model=dict)
async def get_layer7_data(drawing_id: str):
    """Get Layer 7 cost and risk engine data"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    if not drawing.layer7_processed:
        raise HTTPException(status_code=404, detail="Layer 7 data not available")
    
    return {
        "success": True,
        "data": drawing.layer7_data
    }

@router.get("/drawing/{drawing_id}/layer8", response_model=dict)
async def get_layer8_data(drawing_id: str):
    """Get Layer 8 supplier discovery / budget optimization data"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    if not drawing.layer8_processed:
        raise HTTPException(status_code=404, detail="Layer 8 data not available")
    
    return {
        "success": True,
        "data": drawing.layer8_data
    }

@router.get("/drawing/{drawing_id}/layer9", response_model=dict)
async def get_layer9_data(drawing_id: str):
    """Get Layer 9 procurement data"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    if not drawing.layer9_processed:
        raise HTTPException(status_code=404, detail="Layer 9 data not available")
    
    return {
        "success": True,
        "data": drawing.layer9_data
    }

@router.get("/drawing/{drawing_id}/layer10", response_model=dict)
async def get_layer10_data(drawing_id: str):
    """Get Layer 10 scheduling data"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    if not drawing.layer10_processed:
        raise HTTPException(status_code=404, detail="Layer 10 data not available")
    
    return {
        "success": True,
        "data": drawing.layer10_data
    }

@router.get("/drawing/{drawing_id}/preprocessed-image")
async def get_preprocessed_image(drawing_id: str):
    """Get preprocessed image for raster files"""
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    if not drawing.preprocessed_image_path:
        raise HTTPException(status_code=404, detail="Preprocessed image not available")
    
    if not os.path.exists(drawing.preprocessed_image_path):
        raise HTTPException(status_code=404, detail="Preprocessed image file not found")
    
    return FileResponse(drawing.preprocessed_image_path, media_type="image/png")
