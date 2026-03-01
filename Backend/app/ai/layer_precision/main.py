"""Layer 6 Main Pipeline - Precision, Validation & Confidence Engine"""
from typing import Dict, List, Optional
from .cross_view_validator import validate_cross_view
from .redundancy_checker import check_redundancy
from .footprint_validator import validate_footprint
from .steel_ratio_validator import validate_steel_ratio
from .duplicate_detector import detect_duplicates
from .outlier_detector import detect_outliers
from .confidence_engine import aggregate_confidence, propagate_uncertainty

def run_layer6_pipeline(layer4_output: Dict, layer3_output: Optional[Dict] = None) -> Dict:
    """Run complete Layer 6 validation and confidence pipeline
    
    Returns final output structure with validated_qto, flags, confidence, and uncertainty_band
    """
    if not layer4_output.get("success"):
        return {
            "success": False,
            "error": "Layer 4 output invalid"
        }
    
    measurements = layer4_output.get("measurements", [])
    aggregation = layer4_output.get("aggregation", {})
    
    # Run all validation modules
    consistency_results = validate_cross_view(measurements)
    sanity_results = perform_sanity_checks(measurements)
    anomaly_results = detect_outliers(measurements)
    redundancy_results = check_redundancy(measurements)
    duplicate_results = detect_duplicates(measurements)
    footprint_results = validate_footprint(measurements)
    steel_ratio_results = validate_steel_ratio(measurements, aggregation)
    
    # Aggregate confidence
    confidence_results = aggregate_confidence(
        measurements, consistency_results, sanity_results, 
        anomaly_results, redundancy_results, duplicate_results
    )
    
    # Propagate uncertainty
    uncertainty_results = propagate_uncertainty(aggregation, confidence_results)
    
    # Generate flags
    flags = generate_flags(
        consistency_results, sanity_results, anomaly_results,
        redundancy_results, duplicate_results, footprint_results,
        steel_ratio_results
    )
    
    # Calculate overall confidence
    overall_confidence = confidence_results["average_confidence"]
    
    # Calculate uncertainty bands
    uncertainty_band = calculate_uncertainty_band(
        uncertainty_results["aggregation"], overall_confidence
    )
    
    # Generate quality grade
    quality_grade = calculate_quality_grade(
        overall_confidence, consistency_results, sanity_results
    )
    
    # Final output structure
    return {
        "success": True,
        "validated_qto": confidence_results["measurements"],
        "flags": flags,
        "overall_confidence": round(overall_confidence, 2),
        "uncertainty_band": uncertainty_band,
        "validated_aggregation": uncertainty_results["aggregation"],
        "quality_grade": quality_grade,
        "validation_summary": {
            "consistency_checks": consistency_results,
            "sanity_checks": sanity_results,
            "anomaly_detection": anomaly_results,
            "redundancy_checks": redundancy_results,
            "duplicate_detection": duplicate_results,
            "footprint_validation": footprint_results,
            "steel_concrete_ratio": steel_ratio_results
        },
        "confidence_distribution": confidence_results["confidence_distribution"]
    }

def perform_sanity_checks(measurements: List[Dict]) -> Dict:
    """Perform sanity checks on measurement values"""
    RANGES = {
        "Wall": {"thickness": (0.1, 0.6), "height": (2.0, 6.0), "length": (0.5, 50.0)},
        "Slab": {"thickness": (0.1, 0.5), "length": (1.0, 100.0), "width": (1.0, 100.0)},
        "Column": {"width": (0.2, 2.0), "depth": (0.2, 2.0), "height": (2.0, 10.0)},
        "Beam": {"width": (0.2, 1.0), "depth": (0.2, 1.5), "length": (1.0, 20.0)},
        "Door": {"width": (0.6, 3.0), "height": (1.8, 3.0)},
        "Window": {"width": (0.5, 5.0), "height": (0.5, 3.0)}
    }
    
    issues = []
    passed = 0
    
    for m in measurements:
        element_type = m.get("type")
        dims = m.get("dimensions", {})
        
        if element_type not in RANGES:
            continue
        
        ranges = RANGES[element_type]
        
        for dim_name, (min_val, max_val) in ranges.items():
            if dim_name in dims:
                value = dims[dim_name]
                
                if value < min_val or value > max_val:
                    issues.append({
                        "element_id": m.get("element_id"),
                        "type": element_type,
                        "dimension": dim_name,
                        "value": value,
                        "expected_range": [min_val, max_val],
                        "severity": "high" if value < min_val * 0.5 or value > max_val * 2 else "medium"
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

def generate_flags(consistency: Dict, sanity: Dict, anomaly: Dict,
                   redundancy: Dict, duplicate: Dict, footprint: Dict,
                   steel_ratio: Dict) -> List[Dict]:
    """Generate flags from all validation results"""
    flags = []
    
    # Consistency flags
    for issue in consistency["issues"]:
        flags.append({
            "type": "Thickness Mismatch" if "area" in issue["check"] else "Volume Mismatch",
            "element": issue["element_id"],
            "severity": "High" if issue["error_pct"] > 10 else "Medium",
            "details": f"{issue['error_pct']}% deviation"
        })
    
    # Sanity flags
    for issue in sanity["issues"]:
        flags.append({
            "type": "Unrealistic Dimension",
            "element": issue["element_id"],
            "severity": issue["severity"].capitalize(),
            "details": f"{issue['dimension']}: {issue['value']} (expected {issue['expected_range']})"
        })
    
    # Anomaly flags
    for anomaly_item in anomaly["anomalies"]:
        flags.append({
            "type": "Statistical Outlier",
            "element": anomaly_item["element_id"],
            "severity": anomaly_item["severity"].capitalize(),
            "details": f"Z-score: {anomaly_item['z_score']}"
        })
    
    # Redundancy flags
    for issue in redundancy.get("issues", []):
        flags.append({
            "type": "Dimension Mismatch",
            "element": issue["element_id"],
            "severity": issue["severity"].capitalize(),
            "details": f"Scaled vs Text: {issue['deviation_pct']}% deviation"
        })
    
    # Duplicate flags
    for dup in duplicate.get("duplicates", []):
        flags.append({
            "type": "Duplicate Element",
            "element": dup["element_id"],
            "severity": dup["severity"].capitalize(),
            "details": f"Overlaps with {dup['duplicate_of']} ({dup['overlap_ratio']*100}%)"
        })
    
    # Footprint flags
    if footprint.get("flag"):
        flags.append({
            "type": "Footprint Validation",
            "element": "Building",
            "severity": "Medium",
            "details": footprint["flag"]
        })
    
    # Steel ratio flags
    for issue in steel_ratio.get("issues", []):
        flags.append({
            "type": "Steel Ratio Anomaly",
            "element": issue["element_type"],
            "severity": issue["severity"].capitalize(),
            "details": f"Ratio: {issue['ratio']}% (expected {issue['expected_range']}%)"
        })
    
    return flags

def calculate_uncertainty_band(aggregation: Dict, overall_confidence: float) -> Dict:
    """Calculate uncertainty bands for cost and duration"""
    uncertainty_pct = (1 - overall_confidence) * 100
    
    # Estimate duration based on typical productivity
    total_volume = sum(
        data.get("volume_m3", 0) 
        for data in aggregation.values()
    )
    
    # Typical productivity: 10 m³/day
    estimated_duration = total_volume / 10 if total_volume > 0 else 0
    duration_uncertainty = estimated_duration * uncertainty_pct / 100
    
    return {
        "cost": f"±{round(uncertainty_pct, 1)}%",
        "duration": f"±{round(duration_uncertainty, 1)} days"
    }

def calculate_quality_grade(confidence: float, consistency: Dict, sanity: Dict) -> str:
    """Calculate quality grade A-D"""
    if confidence >= 0.85 and consistency["pass_rate"] >= 0.95 and sanity["pass_rate"] >= 0.95:
        return "A"
    elif confidence >= 0.75 and consistency["pass_rate"] >= 0.85 and sanity["pass_rate"] >= 0.85:
        return "B"
    elif confidence >= 0.65:
        return "C"
    else:
        return "D"
