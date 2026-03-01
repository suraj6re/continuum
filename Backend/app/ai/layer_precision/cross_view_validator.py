"""Cross-View Consistency Validator"""
from typing import Dict, List

def validate_cross_view(measurements: List[Dict]) -> Dict:
    """Compare plan-based area, section-based thickness, elevation-based height"""
    issues = []
    passed = 0
    
    for m in measurements:
        element_id = m.get("element_id")
        element_type = m.get("type")
        dims = m.get("dimensions", {})
        meas = m.get("measurements", {})
        
        # Check volume consistency (cross-view)
        if "volume" in meas and all(k in dims for k in ["length", "width", "height"]):
            expected_volume = dims["length"] * dims["width"] * dims["height"]
            actual_volume = meas["volume"]
            error_pct = abs(expected_volume - actual_volume) / expected_volume * 100 if expected_volume > 0 else 0
            
            if error_pct > 5:
                issues.append({
                    "element_id": element_id,
                    "type": element_type,
                    "check": "volume_consistency",
                    "expected": expected_volume,
                    "actual": actual_volume,
                    "error_pct": round(error_pct, 2)
                })
            else:
                passed += 1
        
        # Check area consistency
        if "area" in meas and "length" in dims and "width" in dims:
            expected_area = dims["length"] * dims["width"]
            actual_area = meas["area"]
            error_pct = abs(expected_area - actual_area) / expected_area * 100 if expected_area > 0 else 0
            
            if error_pct > 5:
                issues.append({
                    "element_id": element_id,
                    "type": element_type,
                    "check": "area_consistency",
                    "expected": expected_area,
                    "actual": actual_area,
                    "error_pct": round(error_pct, 2)
                })
            else:
                passed += 1
    
    return {
        "total_checks": passed + len(issues),
        "passed": passed,
        "failed": len(issues),
        "issues": issues,
        "pass_rate": passed / (passed + len(issues)) if (passed + len(issues)) > 0 else 1.0
    }
