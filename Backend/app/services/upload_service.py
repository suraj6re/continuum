import os
import uuid
import aiofiles
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile, HTTPException
from app.models.drawing import Drawing
from app.utils.file_identifier import identify_file_type, is_allowed_file
from app.ai.pipeline import route_preprocessing
from app.ai.layer2_pipeline import run_layer2_pipeline
from app.ai.layer3_pipeline import run_layer3_pipeline
from app.ai.layer4_pipeline import run_layer4_pipeline
from app.ai.layer5_pipeline import run_layer5_pipeline
from app.ai.layer_precision import run_layer6_pipeline

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 52428800))  # 50MB

def convert_numpy_types(obj):
    """Convert numpy types to Python native types for MongoDB serialization"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    return obj

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
        drawing.geometry = convert_numpy_types(result.get('geometry'))
        drawing.bounding_box = convert_numpy_types(result.get('bounding_box'))
        drawing.text = convert_numpy_types(result.get('text'))
        drawing.scale_candidates = convert_numpy_types(result.get('scale_candidates', []))
        drawing.units = convert_numpy_types(result.get('units'))
        drawing.layers = convert_numpy_types(result.get('layers'))
        drawing.blocks = convert_numpy_types(result.get('blocks'))
        drawing.pipeline_type = result.get('pipeline_type')
        drawing.entity_count = convert_numpy_types(result.get('entity_count'))
        drawing.intermediate_json = result.get('intermediate_json')
        
        # Run Layer 2 pipeline if vector
        if result.get('pipeline_type') == 'vector':
            try:
                layer2_result = run_layer2_pipeline(result)
                drawing.layer2_processed = True
                drawing.layer2_data = convert_numpy_types(layer2_result)
                
                # Run Layer 3 pipeline if Layer 2 succeeded
                if layer2_result.get('status') == 'success':
                    try:
                        layer3_result = run_layer3_pipeline(result, layer2_result)
                        drawing.layer3_processed = True
                        drawing.layer3_data = convert_numpy_types(layer3_result)
                        
                        # Run Layer 4 pipeline if Layer 3 succeeded
                        if not layer3_result.get('error'):
                            try:
                                layer4_result = run_layer4_pipeline(layer3_result)
                                drawing.layer4_processed = True
                                drawing.layer4_data = convert_numpy_types(layer4_result)
                                
                                # Run Layer 5 pipeline if Layer 4 succeeded
                                if layer4_result.get('success'):
                                    try:
                                        layer5_result = run_layer5_pipeline(result, layer2_result, layer3_result, layer4_result)
                                        drawing.layer5_processed = True
                                        drawing.layer5_data = convert_numpy_types(layer5_result)
                                        
                                        # Run Layer 6 pipeline if Layer 5 succeeded
                                        if layer5_result.get('success'):
                                            try:
                                                layer6_result = run_layer6_pipeline(layer4_result, layer3_result)
                                                drawing.layer6_processed = True
                                                drawing.layer6_data = convert_numpy_types(layer6_result)
                                            except Exception as e:
                                                print(f"Layer 6 processing failed: {e}")
                                                drawing.layer6_processed = False
                                    except Exception as e:
                                        print(f"Layer 5 processing failed: {e}")
                                        drawing.layer5_processed = False
                            except Exception as e:
                                print(f"Layer 4 processing failed: {e}")
                                drawing.layer4_processed = False
                    except Exception as e:
                        print(f"Layer 3 processing failed: {e}")
                        drawing.layer3_processed = False
            except Exception as e:
                print(f"Layer 2 processing failed: {e}")
                drawing.layer2_processed = False
        
        await drawing.save()
        
    except Exception as e:
        # Store error but don't fail upload
        import traceback
        error_detail = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Processing error: {error_detail}")
        drawing.processed = False
        drawing.processing_error = str(e)
        drawing.status = "error"
        await drawing.save()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    return drawing
