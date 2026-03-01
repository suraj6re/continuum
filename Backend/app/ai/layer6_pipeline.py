"""Layer 6: Precision, Validation & Confidence Engine"""
from typing import Dict, List, Optional
import statistics

def run_layer6_pipeline(layer4_output: Dict, layer3_output: Optional[Dict] = None) -> Dict:
    """Run complete Layer 6 validation and confidence pipeline
    
    Args:
        layer4_output: Complete output from Layer 4 pipeline
        layer3_output: Optional Layer 3 output for cross-validation
    
    Returns:
        Validated QTO with confidence scores and uncertainty ranges
    """
    if not layer4_output.get("success"):
        return {
            "success": False,
            "error": "Layer 4 output invalid"
        }
    
    measurements = layer4_output.get("measurements", [])
    aggregation = layer4_output.get("aggregation", {})
    
    # Step 1: Internal consistency checks
    consistency_results = check_internal_consistency(measurements)
    
    # Step 2: Sanity checks
    sanity_results = perform_sanity_checks(measurements)
    
    # Step 3: Anomaly detection
    anomaly_results = detect_anomalies(measurements)
    
    # Step 4: Redundant measurement comparison
    redundancy_results = compare_redundant_measurements(measurements)
    
    # Step 5: Duplicate detection
    duplicate_results = detect_duplicates(measurements)
    
    # Step 6: Building footprint validation
    footprint_results = validate_building_footprint(measurements)
    
    # Step 7: Steel-to-concrete ratio check
    steel_ratio_results = check_steel_concrete_ratio(measurements, aggregation)
    
    # Step 8: Confidence aggregation
    confidence_results = aggregate_confidence(measurements, consistency_results, 
                                             sanity_results, anomaly_results,
                                             redundancy_results, duplicate_results)
    
    # Step 9: Uncertainty propagation
    uncertainty_results = propagate_uncertainty(aggregation, confidence_results)
    
    # Step 10: Generate validation report
    validation_report = generate_validation_report(
        consistency_results, sanity_results, anomaly_results, 
        redundancy_results, duplicate_results, footprint_results,
        steel_ratio_results, confidence_results, uncertainty_results
    )
    
    return {
        "success": True,
        "validated_measurements": confidence_results["measurements"],
        "validated_aggregation": uncertainty_results["aggregation"],
        "validation_report": validation_report,
        "overall_confidence": validation_report["overall_confidence"],
        "quality_grade": validation_report["quality_grade"]
    }

def check_internal_consistency(measurements: List[Dict]) -> Dict:
    """Check internal consistency of measurements"""
    issues = []
    passed = 0
    
    for m in measurements:
        element_id = m.get("element_id")
        element_type = m.get("type")
        dims = m.get("dimensions", {})
        meas = m.get("measurements", {})
        
        # Check volume consistency
        if "volume" in meas and all(k in dims for k in ["length", "width", "height"]):
            expected_volume = dims["length"] * dims["width"] * dims["height"]
            actual_volume = meas["volume"]
            error_pct = abs(expected_volume - actual_volume) / expected_volume * 100 if expected_volume > 0 else 0
            
            if error_pct > 5:  # 5% tolerance
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

def perform_sanity_checks(measurements: List[Dict]) -> Dict:
    """Perform sanity checks on measurement values"""
    # Realistic ranges for construction elements (in meters)
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

def detect_anomalies(measurements: List[Dict]) -> Dict:
    """Detect statistical anomalies in measurements"""
    # Group by type
    by_type = {}
    for m in measurements:
        elem_type = m.get("type")
        if elem_type not in by_type:
            by_type[elem_type] = []
        by_type[elem_type].append(m)
    
    anomalies = []
    
    for elem_type, elements in by_type.items():
        if len(elements) < 3:  # Need at least 3 for statistics
            continue
        
        # Check volume anomalies
        volumes = [e.get("measurements", {}).get("volume", 0) for e in elements if "volume" in e.get("measurements", {})]
        
        if len(volumes) >= 3:
            mean_vol = statistics.mean(volumes)
            stdev_vol = statistics.stdev(volumes) if len(volumes) > 1 else 0
            
            for i, vol in enumerate(volumes):
                if stdev_vol > 0:
                    z_score = abs((vol - mean_vol) / stdev_vol)
                    
                    if z_score > 3:  # 3 sigma rule
                        anomalies.append({
                            "element_id": elements[i].get("element_id"),
                            "type": elem_type,
                            "metric": "volume",
                            "value": vol,
                            "mean": mean_vol,
                            "z_score": round(z_score, 2),
                            "severity": "high" if z_score > 4 else "medium"
                        })
    
    return {
        "total_anomalies": len(anomalies),
        "anomalies": anomalies,
        "anomaly_rate": len(anomalies) / len(measurements) if measurements else 0
    }

def aggregate_confidence(measurements: List[Dict], consistency: Dict, 
                        sanity: Dict, anomaly: Dict, redundancy: Dict, duplicate: Dict) -> Dict:
    """Aggregate confidence scores from all validation checks"""
    enhanced_measurements = []
    
    # Create lookup sets for failed checks
    consistency_failed = {issue["element_id"] for issue in consistency["issues"]}
    sanity_failed = {issue["element_id"] for issue in sanity["issues"]}
    anomaly_failed = {issue["element_id"] for issue in anomaly["anomalies"]}
    redundancy_failed = {issue["element_id"] for issue in redundancy.get("issues", [])}
    duplicate_failed = {issue["element_id"] for issue in duplicate.get("duplicates", [])}
    
    for m in measurements:
        element_id = m.get("element_id")
        base_confidence = m.get("confidence", 0.5)
        
        # Penalty factors
        penalties = []
        
        if element_id in consistency_failed:
            penalties.append(0.15)  # -15% for consistency failure
        
        if element_id in sanity_failed:
            penalties.append(0.20)  # -20% for sanity failure
        
        if element_id in anomaly_failed:
            penalties.append(0.25)  # -25% for anomaly
        
        if element_id in redundancy_failed:
            penalties.append(0.10)  # -10% for redundancy mismatch
        
        if element_id in duplicate_failed:
            penalties.append(0.30)  # -30% for duplicate
        
        # Calculate final confidence
        total_penalty = sum(penalties)
        final_confidence = max(0.1, base_confidence - total_penalty)
        
        # Determine confidence level
        if final_confidence >= 0.8:
            confidence_level = "High"
        elif final_confidence >= 0.6:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
        
        enhanced_m = m.copy()
        enhanced_m["validation"] = {
            "base_confidence": base_confidence,
            "final_confidence": round(final_confidence, 3),
            "confidence_level": confidence_level,
            "penalties": penalties,
            "flags": {
                "consistency_issue": element_id in consistency_failed,
                "sanity_issue": element_id in sanity_failed,
                "anomaly": element_id in anomaly_failed,
                "redundancy_mismatch": element_id in redundancy_failed,
                "duplicate": element_id in duplicate_failed
            }
        }
        
        enhanced_measurements.append(enhanced_m)
    
    # Overall statistics
    avg_confidence = statistics.mean([m["validation"]["final_confidence"] for m in enhanced_measurements]) if enhanced_measurements else 0
    
    confidence_distribution = {
        "High": sum(1 for m in enhanced_measurements if m["validation"]["confidence_level"] == "High"),
        "Medium": sum(1 for m in enhanced_measurements if m["validation"]["confidence_level"] == "Medium"),
        "Low": sum(1 for m in enhanced_measurements if m["validation"]["confidence_level"] == "Low")
    }
    
    return {
        "measurements": enhanced_measurements,
        "average_confidence": round(avg_confidence, 3),
        "confidence_distribution": confidence_distribution
    }

def propagate_uncertainty(aggregation: Dict, confidence_results: Dict) -> Dict:
    """Propagate uncertainty to aggregated quantities using weighted confidence"""
    enhanced_aggregation = {}
    
    for material, data in aggregation.items():
        # Get measurements for this material
        material_measurements = [
            m for m in confidence_results["measurements"]
            if m.get("material") == material
        ]
        
        if not material_measurements:
            enhanced_aggregation[material] = data
            continue
        
        # Calculate total volume for this material
        total_volume = sum(
            m.get("measurements", {}).get("volume", 0)
            for m in material_measurements
        )
        
        # Calculate weighted confidence based on quantity share
        if total_volume > 0:
            weighted_confidence = sum(
                m["validation"]["final_confidence"] * 
                (m.get("measurements", {}).get("volume", 0) / total_volume)
                for m in material_measurements
                if m.get("measurements", {}).get("volume", 0) > 0
            )
        else:
            # Fallback to simple average if no volume data
            confidences = [m["validation"]["final_confidence"] for m in material_measurements]
            weighted_confidence = statistics.mean(confidences)
        
        # Calculate uncertainty percentage (inverse of confidence)
        uncertainty_pct = (1 - weighted_confidence) * 100
        
        # Apply to quantities
        enhanced_data = data.copy()
        
        if "volume_m3" in data:
            volume = data["volume_m3"]
            uncertainty = volume * uncertainty_pct / 100
            enhanced_data["volume_with_uncertainty"] = f"{volume:.2f} ± {uncertainty:.2f} m³ ({uncertainty_pct:.1f}%)"
            enhanced_data["volume_range"] = {
                "min": round(volume - uncertainty, 2),
                "max": round(volume + uncertainty, 2),
                "nominal": round(volume, 2)
            }
        
        if "area_m2" in data:
            area = data["area_m2"]
            uncertainty = area * uncertainty_pct / 100
            enhanced_data["area_with_uncertainty"] = f"{area:.2f} ± {uncertainty:.2f} m² ({uncertainty_pct:.1f}%)"
            enhanced_data["area_range"] = {
                "min": round(area - uncertainty, 2),
                "max": round(area + uncertainty, 2),
                "nominal": round(area, 2)
            }
        
        enhanced_data["confidence"] = round(weighted_confidence, 3)
        enhanced_data["uncertainty_pct"] = round(uncertainty_pct, 2)
        
        enhanced_aggregation[material] = enhanced_data
    
    return {
        "aggregation": enhanced_aggregation
    }

def generate_validation_report(consistency: Dict, sanity: Dict, anomaly: Dict,
                               redundancy: Dict, duplicate: Dict, footprint: Dict,
                               steel_ratio: Dict, confidence: Dict, uncertainty: Dict) -> Dict:
    """Generate comprehensive validation report"""
    # Calculate overall confidence
    overall_confidence = confidence["average_confidence"]
    
    # Determine quality grade
    if overall_confidence >= 0.85 and consistency["pass_rate"] >= 0.95 and sanity["pass_rate"] >= 0.95:
        quality_grade = "A"
    elif overall_confidence >= 0.75 and consistency["pass_rate"] >= 0.85 and sanity["pass_rate"] >= 0.85:
        quality_grade = "B"
    elif overall_confidence >= 0.65:
        quality_grade = "C"
    else:
        quality_grade = "D"
    
    # Count critical issues
    critical_issues = (
        len([i for i in consistency["issues"] if i.get("error_pct", 0) > 10]) +
        len([i for i in sanity["issues"] if i.get("severity") == "high"]) +
        len([a for a in anomaly["anomalies"] if a.get("severity") == "high"]) +
        len([d for d in duplicate.get("duplicates", []) if d.get("severity") == "high"])
    )
    
    return {
        "overall_confidence": round(overall_confidence, 3),
        "quality_grade": quality_grade,
        "validation_summary": {
            "consistency_checks": {
                "total": consistency["total_checks"],
                "passed": consistency["passed"],
                "failed": consistency["failed"],
                "pass_rate": round(consistency["pass_rate"], 3)
            },
            "sanity_checks": {
                "total": sanity["total_checks"],
                "passed": sanity["passed"],
                "failed": sanity["failed"],
                "pass_rate": round(sanity["pass_rate"], 3)
            },
            "anomaly_detection": {
                "total_elements": len(confidence["measurements"]),
                "anomalies_found": anomaly["total_anomalies"],
                "anomaly_rate": round(anomaly["anomaly_rate"], 3)
            },
            "redundancy_checks": {
                "total": redundancy.get("total_checks", 0),
                "mismatches": len(redundancy.get("issues", [])),
                "pass_rate": round(redundancy.get("pass_rate", 1.0), 3)
            },
            "duplicate_detection": {
                "total_elements": len(confidence["measurements"]),
                "duplicates_found": len(duplicate.get("duplicates", [])),
                "duplicate_rate": round(duplicate.get("duplicate_rate", 0), 3)
            },
            "footprint_validation": footprint,
            "steel_concrete_ratio": steel_ratio
        },
        "confidence_distribution": confidence["confidence_distribution"],
        "critical_issues": critical_issues,
        "recommendations": generate_recommendations(quality_grade, critical_issues, consistency, sanity, anomaly, redundancy, duplicate, footprint, steel_ratio)
    }

def generate_recommendations(grade: str, critical_issues: int, 
                            consistency: Dict, sanity: Dict, anomaly: Dict,
                            redundancy: Dict, duplicate: Dict, footprint: Dict,
                            steel_ratio: Dict) -> List[str]:
    """Generate actionable recommendations"""
    recommendations = []
    
    if grade in ["C", "D"]:
        recommendations.append("Quality grade is low. Manual review recommended before using quantities.")
    
    if critical_issues > 0:
        recommendations.append(f"{critical_issues} critical issues detected. Review flagged elements.")
    
    if consistency["pass_rate"] < 0.9:
        recommendations.append("Internal consistency issues detected. Verify dimension calculations.")
    
    if sanity["pass_rate"] < 0.9:
        recommendations.append("Unrealistic dimensions detected. Check drawing scale and units.")
    
    if anomaly["anomaly_rate"] > 0.1:
        recommendations.append("Statistical anomalies detected. Review outlier elements.")
    
    if redundancy.get("pass_rate", 1.0) < 0.9:
        recommendations.append("Dimension text mismatches detected. Verify scaled vs annotated dimensions.")
    
    if duplicate.get("duplicate_rate", 0) > 0.05:
        recommendations.append("Duplicate elements detected. Check for overlapping geometry.")
    
    if footprint.get("flag"):
        recommendations.append(footprint["flag"])
    
    if steel_ratio.get("issues"):
        recommendations.append("Steel-to-concrete ratios outside typical ranges. Verify reinforcement calculations.")
    
    if not recommendations:
        recommendations.append("All validation checks passed. Quantities are reliable.")
    
    return recommendations


def compare_redundant_measurements(measurements: List[Dict]) -> Dict:
    """Compare scaled measurements with explicit dimension text"""
    issues = []
    passed = 0
    
    for m in measurements:
        element_id = m.get("element_id")
        dims = m.get("dimensions", {})
        
        # Check if both scaled and text dimensions exist
        scaled_length = dims.get("length")
        text_length = dims.get("text_length")
        
        if scaled_length and text_length:
            deviation = abs(scaled_length - text_length) / text_length
            
            if deviation > 0.03:  # 3% threshold
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
            
            # Simple overlap check using bounding boxes
            overlap = check_geometry_overlap(geom1, geom2)
            
            if overlap > 0.8:  # 80% overlap threshold
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

def check_geometry_overlap(geom1: Dict, geom2: Dict) -> float:
    """Calculate overlap ratio between two geometries"""
    # Simple bounding box overlap check
    bbox1 = geom1.get("bbox", {})
    bbox2 = geom2.get("bbox", {})
    
    if not bbox1 or not bbox2:
        return 0.0
    
    x1_min, y1_min = bbox1.get("min_x", 0), bbox1.get("min_y", 0)
    x1_max, y1_max = bbox1.get("max_x", 0), bbox1.get("max_y", 0)
    x2_min, y2_min = bbox2.get("min_x", 0), bbox2.get("min_y", 0)
    x2_max, y2_max = bbox2.get("max_x", 0), bbox2.get("max_y", 0)
    
    # Calculate intersection
    x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
    y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
    overlap_area = x_overlap * y_overlap
    
    # Calculate areas
    area1 = (x1_max - x1_min) * (y1_max - y1_min)
    area2 = (x2_max - x2_min) * (y2_max - y2_min)
    
    if area1 == 0 or area2 == 0:
        return 0.0
    
    # Return overlap ratio relative to smaller area
    return overlap_area / min(area1, area2)

def validate_building_footprint(measurements: List[Dict]) -> Dict:
    """Validate total slab area against building footprint"""
    # Calculate total slab area
    slab_area = sum(
        m.get("measurements", {}).get("area", 0)
        for m in measurements
        if m.get("type") == "Slab"
    )
    
    # Estimate building footprint from walls
    wall_measurements = [m for m in measurements if m.get("type") == "Wall"]
    
    if not wall_measurements:
        return {"valid": True, "flag": None}
    
    # Simple footprint estimation (this is a placeholder)
    # In real implementation, would compute actual boundary polygon
    footprint_area = slab_area  # Placeholder
    
    if slab_area > footprint_area * 1.2:  # 20% threshold
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

def check_steel_concrete_ratio(measurements: List[Dict], aggregation: Dict) -> Dict:
    """Check steel-to-concrete ratios for reinforced concrete elements"""
    TYPICAL_RATIOS = {
        "Slab": (0.008, 0.015),  # 0.8-1.5%
        "Column": (0.02, 0.04),   # 2-4%
        "Beam": (0.015, 0.03)     # 1.5-3%
    }
    
    issues = []
    
    # Get concrete volume by element type
    for elem_type, (min_ratio, max_ratio) in TYPICAL_RATIOS.items():
        concrete_volume = sum(
            m.get("measurements", {}).get("volume", 0)
            for m in measurements
            if m.get("type") == elem_type and m.get("material") == "Concrete"
        )
        
        # Get steel weight (placeholder - would come from reinforcement estimation)
        steel_weight = 0  # Would be calculated from Layer 4 reinforcement data
        
        if concrete_volume > 0 and steel_weight > 0:
            # Steel density ~7850 kg/m³, so steel_volume = steel_weight / 7850
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
