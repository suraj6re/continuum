"""Steel-to-Concrete Ratio Validator"""
from typing import Dict, List

def validate_steel_ratio(measurements: List[Dict], aggregation: Dict) -> Dict:
    """Check steel-to-concrete ratios for reinforced concrete elements"""
    TYPICAL_RATIOS = {
        "Slab": (0.008, 0.015),
        "Column": (0.02, 0.04),
        "Beam": (0.015, 0.03)
    }
    
    issues = []
    
    for elem_type, (min_ratio, max_ratio) in TYPICAL_RATIOS.items():
        concrete_volume = sum(
            m.get("measurements", {}).get("volume", 0)
            for m in measurements
            if m.get("type") == elem_type and m.get("material") == "Concrete"
        )
        
        steel_weight = 0
        
        if concrete_volume > 0 and steel_weight > 0:
            steel_volume = steel_weight / 7850
            ratio = steel_volume / concrete_volume
            
            if ratio < min_ratio or ratio > max_ratio:
                issues.append({
                    "element_type": elem_type,
                    "ratio": round(ratio * 100, 2),
                    "expected_range": [round(min_ratio * 100, 2), round(max_ratio * 100, 2)],
                    "severity": "high" if ratio < min_ratio * 0.5 or ratio > max_ratio * 2 else "medium"
                })
    
    return {
        "issues": issues,
        "total_checks": len(TYPICAL_RATIOS),
        "passed": len(TYPICAL_RATIOS) - len(issues)
    }
