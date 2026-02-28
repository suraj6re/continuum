from fastapi import APIRouter, HTTPException
from app.services.analysis_service import analyze_drawing

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.post("/drawing/{drawing_id}", response_model=dict)
async def analyze_drawing_endpoint(drawing_id: str):
    """
    Trigger analysis for uploaded drawing
    """
    try:
        result = await analyze_drawing(drawing_id)
        return {
            "success": True,
            "message": "Analysis completed",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/drawing/{drawing_id}/status", response_model=dict)
async def get_analysis_status(drawing_id: str):
    """
    Get analysis status for a drawing
    """
    from app.models.drawing import Drawing
    
    drawing = await Drawing.get(drawing_id)
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
    
    return {
        "success": True,
        "data": {
            "drawing_id": str(drawing.id),
            "status": drawing.status,
            "filename": drawing.original_filename
        }
    }
