import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict
import os
from app.ai.raster_pipeline import run_raster_pipeline
from app.ai.dxf_enhanced import process_dxf_enhanced
from app.ai.svg_enhanced import parse_svg_enhanced
from app.ai.intermediate_utils import save_intermediate_representation, extract_scale_candidates
from app.ai.dwg_converter import convert_dwg_to_dxf

RASTER_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.img'}
VECTOR_EXTENSIONS = {'.dxf', '.dwg'}
PDF_EXTENSION = '.pdf'

def route_preprocessing(file_path: str, file_type: str) -> Dict:
    """
    Route file to appropriate preprocessing pipeline based on type
    """
    
    file_ext = Path(file_path).suffix.lower()
    file_type_upper = file_type.upper()
    
    # Raster pipeline
    if file_ext in RASTER_EXTENSIONS or file_type_upper in ['PNG', 'JPG', 'JPEG']:
        result = run_raster_pipeline(file_path)
    
    # Vector pipeline - DXF
    elif file_ext == '.dxf' or file_type_upper == 'DXF':
        result = process_dxf_enhanced(file_path)
    
    # Vector pipeline - DWG
    elif file_ext == '.dwg' or file_type_upper == 'DWG':
        dxf_path = convert_dwg_to_dxf(file_path)
        result = process_dxf_enhanced(dxf_path)
    
    # PDF - needs detection
    elif file_ext == PDF_EXTENSION or file_type_upper == 'PDF':
        if is_vector_pdf(file_path):
            result = process_vector_pdf_svg(file_path)
        else:
            result = run_raster_pipeline(file_path)
    
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    # STEP 10: Extract scale candidates from text
    if 'text' in result and result.get('pipeline_type') == 'vector':
        scale_candidates = extract_scale_candidates(result['text'])
        result['scale_candidates'] = scale_candidates
    
    # STEP 9: Save intermediate representation
    try:
        json_path = save_intermediate_representation(result, file_path)
        result['intermediate_json'] = json_path
    except Exception as e:
        print(f"Warning: Could not save intermediate JSON: {e}")
    
    return result

def is_vector_pdf(file_path: str) -> bool:
    """
    Detect if PDF contains vector objects or is image-based
    """
    try:
        doc = fitz.open(file_path)
        
        # Check first page
        page = doc[0]
        
        # Get drawing commands
        drawings = page.get_drawings()
        
        # Get images
        images = page.get_images()
        
        doc.close()
        
        # If has vector drawings and few/no images, it's vector
        if len(drawings) > 10 and len(images) < 2:
            return True
        
        # If mostly images, it's raster
        return False
    
    except Exception as e:
        print(f"PDF detection error: {e}")
        return False

def process_vector_pdf_svg(file_path: str) -> Dict:
    """Process vector PDF using SVG conversion"""
    try:
        doc = fitz.open(file_path)
        page = doc[0]
        
        # Get page dimensions
        page_rect = page.rect
        page_height = page_rect.height
        
        # Extract text blocks from PDF
        text_instances = page.get_text("dict")
        text_entities = []
        
        for block in text_instances.get('blocks', []):
            if block.get('type') == 0:  # text block
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        bbox = span.get('bbox', [0, 0, 0, 0])
                        text_entities.append({
                            'text': span.get('text', ''),
                            'position': [bbox[0], bbox[1]],
                            'layer': '0'
                        })
        
        # Convert to SVG
        svg_data = page.get_svg_image()
        doc.close()
        
        # Parse SVG with enhanced parser
        result = parse_svg_enhanced(svg_data, page_height)
        
        # Merge PDF text with SVG text
        result['text'].extend(text_entities)
        
        return result
    
    except Exception as e:
        raise ValueError(f"Failed to process vector PDF: {str(e)}")
    """
    Extract vector data from PDF
    """
    try:
        doc = fitz.open(file_path)
        page = doc[0]
        
        # Extract paths/drawings
        drawings = page.get_drawings()
        
        lines = []
        shapes = []
        
        for drawing in drawings:
            if 'items' in drawing:
                for item in drawing['items']:
                    if item[0] == 'l':  # line
                        lines.append({
                            'start': [item[1].x, item[1].y],
                            'end': [item[2].x, item[2].y]
                        })
                    elif item[0] == 're':  # rectangle
                        shapes.append({
                            'type': 'rectangle',
                            'rect': [item[1].x, item[1].y, item[1].width, item[1].height]
                        })
        
        # Extract text
        text_instances = page.get_text("dict")
        text_entities = []
        
        for block in text_instances.get('blocks', []):
            if block.get('type') == 0:  # text block
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        text_entities.append({
                            'text': span.get('text', ''),
                            'position': [span.get('bbox', [0,0,0,0])[0], span.get('bbox', [0,0,0,0])[1]],
                            'size': span.get('size', 0)
                        })
        
        doc.close()
        
        return {
            'geometry': {
                'lines': lines,
                'shapes': shapes
            },
            'text': text_entities,
            'units': {'unit': 'points', 'scale': 0.0254/72},  # PDF points to meters
            'pipeline_type': 'vector'
        }
    
    except Exception as e:
        raise ValueError(f"Failed to process vector PDF: {str(e)}")
