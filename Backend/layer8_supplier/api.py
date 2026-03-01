from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from main import run_supplier_discovery
import re

app = FastAPI(title="Layer 9 - Supplier Discovery API")

class SupplierRequest(BaseModel):
    material: str
    grade: Optional[str] = ""
    unit: Optional[str] = ""
    max_distance_km: Optional[int] = 30
    
class Layer8Input(BaseModel):
    """Accept Layer 8 output format"""
    description: str
    unit: str
    quantity: float

def extract_material_grade(description):
    """Extract material and grade from description"""
    desc_lower = description.lower()
    
    # Extract material
    material = None
    if any(word in desc_lower for word in ["steel", "reinforcement", "fe500", "fe415", "tmt"]):
        material = "steel"
    elif any(word in desc_lower for word in ["concrete", "rcc", "m25", "m20", "m30"]):
        material = "concrete"
    elif "cement" in desc_lower:
        material = "cement"
    elif "brick" in desc_lower:
        material = "brick"
    
    # Extract grade
    grade = ""
    grade_match = re.search(r"\b(m\d+|fe\d+)\b", desc_lower)
    if grade_match:
        grade = grade_match.group(1)
    
    return material, grade

@app.post("/find_supplier")
def find_supplier(request: SupplierRequest):
    """
    Find best supplier based on material, grade, and distance
    """
    try:
        result = run_supplier_discovery(
            material=request.material,
            grade=request.grade,
            unit=request.unit,
            max_distance_km=request.max_distance_km
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/find_supplier_from_layer8")
def find_supplier_from_layer8(request: Layer8Input):
    """
    Accept Layer 8 output and find best supplier
    Automatically extracts material and grade from description
    """
    try:
        # Extract material and grade from description
        material, grade = extract_material_grade(request.description)
        
        if not material:
            raise HTTPException(
                status_code=400, 
                detail="Could not identify material from description"
            )
        
        result = run_supplier_discovery(
            material=material,
            grade=grade,
            unit=request.unit,
            max_distance_km=30
        )
        
        # Add Layer 8 context to response
        result["layer8_input"] = {
            "description": request.description,
            "quantity": request.quantity,
            "unit": request.unit,
            "extracted_material": material,
            "extracted_grade": grade
        }
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {
        "message": "Layer 9 - Supplier Discovery API",
        "endpoints": {
            "/find_supplier": "Find supplier by material/grade/unit",
            "/find_supplier_from_layer8": "Accept Layer 8 output format"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy", "layer": 9}
