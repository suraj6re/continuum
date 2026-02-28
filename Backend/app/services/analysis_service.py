from app.models.drawing import Drawing
from app.ai.pipeline import route_preprocessing

async def analyze_drawing(drawing_id: str) -> dict:
    """
    Analyze uploaded drawing using appropriate pipeline
    """
    
    # Get drawing from database
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise ValueError("Drawing not found")
    
    # Update status
    drawing.status = "analyzing"
    await drawing.save()
    
    try:
        # Route to appropriate pipeline
        result = route_preprocessing(drawing.file_path, drawing.file_type)
        
        # Update drawing with results
        drawing.status = "analyzed"
        await drawing.save()
        
        return {
            'drawing_id': str(drawing.id),
            'pipeline_type': result['pipeline_type'],
            'geometry': result['geometry'],
            'text': result.get('text') or result.get('parsed_text'),
            'scale': result.get('scale') or result.get('units'),
            'status': 'success'
        }
    
    except Exception as e:
        drawing.status = "failed"
        await drawing.save()
        raise ValueError(f"Analysis failed: {str(e)}")
