"""Duplicate Element Detector"""
from typing import Dict, List

def detect_duplicates(measurements: List[Dict]) -> Dict:
    """Detect duplicate elements with overlapping geometry"""
    duplicates = []
    checked = set()
    
    for i, m1 in enumerate(measurements):
        if i in checked:
            continue
        
        elem_type = m1.get("type")
        geom1 = m1.get("geometry", {})
        
        if not geom1:
            continue
        
        for j, m2 in enumerate(measurements[i+1:], start=i+1):
            if j in checked or m2.get("type") != elem_type:
                continue
            
            geom2 = m2.get("geometry", {})
            
            if not geom2:
                continue
            
            overlap = check_overlap(geom1, geom2)
            
            if overlap > 0.8:
                duplicates.append({
                    "element_id": m1.get("element_id"),
                    "duplicate_of": m2.get("element_id"),
                    "type": elem_type,
                    "overlap_ratio": round(overlap, 2),
                    "severity": "high" if overlap > 0.95 else "medium"
                })
                checked.add(j)
    
    return {
        "duplicates": duplicates,
        "duplicate_rate": len(duplicates) / len(measurements) if measurements else 0
    }

def check_overlap(geom1: Dict, geom2: Dict) -> float:
    """Calculate overlap ratio between two geometries"""
    bbox1 = geom1.get("bbox", {})
    bbox2 = geom2.get("bbox", {})
    
    if not bbox1 or not bbox2:
        return 0.0
    
    x1_min, y1_min = bbox1.get("min_x", 0), bbox1.get("min_y", 0)
    x1_max, y1_max = bbox1.get("max_x", 0), bbox1.get("max_y", 0)
    x2_min, y2_min = bbox2.get("min_x", 0), bbox2.get("min_y", 0)
    x2_max, y2_max = bbox2.get("max_x", 0), bbox2.get("max_y", 0)
    
    x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
    y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
    overlap_area = x_overlap * y_overlap
    
    area1 = (x1_max - x1_min) * (y1_max - y1_min)
    area2 = (x2_max - x2_min) * (y2_max - y2_min)
    
    if area1 == 0 or area2 == 0:
        return 0.0
    
    return overlap_area / min(area1, area2)
