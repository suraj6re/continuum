"""Redundant Measurement Checker"""
from typing import Dict, List

def check_redundancy(measurements: List[Dict]) -> Dict:
    """Compare scaled measurements with explicit dimension text"""
    issues = []
    passed = 0
    
    for m in measurements:
        element_id = m.get("element_id")
        dims = m.get("dimensions", {})
        
        scaled_length = dims.get("length")
        text_length = dims.get("text_length")
        
        if scaled_length and text_length:
            deviation = abs(scaled_length - text_length) / text_length
            
            if deviation > 0.03:
                issues.append({
                    "element_id": element_id,
                    "type": m.get("type"),
                    "dimension": "length",
                    "scaled_value": scaled_length,
                    "text_value": text_length,
                    "deviation_pct": round(deviation * 100, 2),
                    "severity": "high" if deviation > 0.10 else "medium"
                })
            else:
                passed += 1
    
    return {
        "total_checks": passed + len(issues),
        "passed": passed,
        "issues": issues,
        "pass_rate": passed / (passed + len(issues)) if (passed + len(issues)) > 0 else 1.0
    }
