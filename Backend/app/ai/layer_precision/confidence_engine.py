"""Confidence Aggregation Engine"""
from typing import Dict, List
import statistics

def aggregate_confidence(measurements: List[Dict], consistency: Dict, 
                        sanity: Dict, anomaly: Dict, redundancy: Dict, 
                        duplicate: Dict) -> Dict:
    """Aggregate confidence scores from all validation checks"""
    enhanced_measurements = []
    
    consistency_failed = {issue["element_id"] for issue in consistency["issues"]}
    sanity_failed = {issue["element_id"] for issue in sanity["issues"]}
    anomaly_failed = {issue["element_id"] for issue in anomaly["anomalies"]}
    redundancy_failed = {issue["element_id"] for issue in redundancy.get("issues", [])}
    duplicate_failed = {issue["element_id"] for issue in duplicate.get("duplicates", [])}
    
    for m in measurements:
        element_id = m.get("element_id")
        base_confidence = m.get("confidence", 0.5)
        
        penalties = []
        
        if element_id in consistency_failed:
            penalties.append(0.15)
        if element_id in sanity_failed:
            penalties.append(0.20)
        if element_id in anomaly_failed:
            penalties.append(0.25)
        if element_id in redundancy_failed:
            penalties.append(0.10)
        if element_id in duplicate_failed:
            penalties.append(0.30)
        
        total_penalty = sum(penalties)
        final_confidence = max(0.1, base_confidence - total_penalty)
        
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
    """Propagate uncertainty using weighted confidence"""
    enhanced_aggregation = {}
    
    for material, data in aggregation.items():
        material_measurements = [
            m for m in confidence_results["measurements"]
            if m.get("material") == material
        ]
        
        if not material_measurements:
            enhanced_aggregation[material] = data
            continue
        
        total_volume = sum(
            m.get("measurements", {}).get("volume", 0)
            for m in material_measurements
        )
        
        if total_volume > 0:
            weighted_confidence = sum(
                m["validation"]["final_confidence"] * 
                (m.get("measurements", {}).get("volume", 0) / total_volume)
                for m in material_measurements
                if m.get("measurements", {}).get("volume", 0) > 0
            )
        else:
            confidences = [m["validation"]["final_confidence"] for m in material_measurements]
            weighted_confidence = statistics.mean(confidences)
        
        uncertainty_pct = (1 - weighted_confidence) * 100
        
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
