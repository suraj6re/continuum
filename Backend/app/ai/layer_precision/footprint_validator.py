"""Building Footprint Validator"""
from typing import Dict, List

def validate_footprint(measurements: List[Dict]) -> Dict:
    """Validate total slab area against building footprint"""
    slab_area = sum(
        m.get("measurements", {}).get("area", 0)
        for m in measurements
        if m.get("type") == "Slab"
    )
    
    wall_measurements = [m for m in measurements if m.get("type") == "Wall"]
    
    if not wall_measurements:
        return {"valid": True, "flag": None}
    
    footprint_area = slab_area
    
    if slab_area > footprint_area * 1.2:
        return {
            "valid": False,
            "flag": "Slab area exceeds building footprint by >20%. Check for duplicate slabs.",
            "slab_area": round(slab_area, 2),
            "footprint_area": round(footprint_area, 2),
            "ratio": round(slab_area / footprint_area, 2) if footprint_area > 0 else 0
        }
    
    return {
        "valid": True,
        "flag": None,
        "slab_area": round(slab_area, 2),
        "footprint_area": round(footprint_area, 2)
    }
