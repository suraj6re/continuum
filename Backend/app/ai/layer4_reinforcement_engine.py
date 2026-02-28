"""Layer 4 Step B3: Reinforcement Estimation Engine"""
from typing import Dict, List, Optional
from app.ai.layer4_reinforcement_config import get_reinforcement_ratio, get_ratio_value
from app.ai.layer4_reinforcement_registry import is_eligible_for_reinforcement

def estimate_reinforcement(measurement_output: Dict, 
                          project_config: Optional[Dict] = None) -> Dict:
    """Estimate reinforcement steel for concrete elements using ratio-based method
    
    Formula: steel_kg = concrete_volume × steel_ratio
    
    Args:
        measurement_output: Output from Layer 4 Step 2 (measurements)
        project_config: Optional project-specific ratio overrides
    
    Returns:
        Reinforcement estimation results with formula traces
    """
    if not measurement_output.get("success"):
        return {
            "success": False,
            "error": "Input measurement failed",
            "reinforcement_estimation": [],
            "skipped": []
        }
    
    element_measurements = measurement_output.get("element_measurements", [])
    
    reinforcement_results = []
    skipped = []
    errors = []
    
    # Process each element
    for element in element_measurements:
        element_id = element.get("element_id", "unknown")
        element_type = element.get("type", "unknown")
        
        try:
            # Check eligibility
            eligible, reason = is_eligible_for_reinforcement(element)
            
            if not eligible:
                skipped.append({
                    "element_id": element_id,
                    "type": element_type,
                    "reason": reason
                })
                continue
            
            # Get volume
            measurements = element.get("measurements", {})
            volume = measurements.get("volume")
            
            # Get reinforcement ratio
            ratio_config = get_reinforcement_ratio(element_type, project_config)
            
            if not ratio_config:
                skipped.append({
                    "element_id": element_id,
                    "type": element_type,
                    "reason": "no_ratio_configured"
                })
                continue
            
            steel_ratio = ratio_config["steel_ratio"]
            
            # Calculate steel quantity
            steel_kg = volume * steel_ratio
            
            # Build result with formula trace
            reinforcement_results.append({
                "element_id": element_id,
                "type": element_type,
                "reinforcement": {
                    "steel_kg": round(steel_kg, 2),
                    "ratio_used": steel_ratio,
                    "unit": "kg"
                },
                "formula_trace": {
                    "method": "ratio_based_estimation",
                    "formula": "steel_kg = concrete_volume × steel_ratio",
                    "inputs": {
                        "concrete_volume_m3": round(volume, 4),
                        "steel_ratio_kg_per_m3": steel_ratio
                    },
                    "calculation": f"{volume:.4f} × {steel_ratio} = {steel_kg:.2f} kg",
                    "ratio_source": "project_config" if project_config and element_type in project_config else "default"
                },
                "quality_score": element.get("quality_score", 0.5),
                "confidence": element.get("confidence", 0.5)
            })
        
        except Exception as e:
            errors.append({
                "element_id": element_id,
                "type": element_type,
                "error": str(e)
            })
    
    # Compute statistics
    statistics = _compute_reinforcement_statistics(reinforcement_results, skipped, 
                                                   errors, len(element_measurements))
    
    return {
        "success": True,
        "reinforcement_estimation": reinforcement_results,
        "skipped": skipped,
        "errors": errors,
        "statistics": statistics
    }

def _compute_reinforcement_statistics(results: List[Dict], skipped: List[Dict],
                                      errors: List[Dict], total_elements: int) -> Dict:
    """Compute reinforcement estimation statistics
    
    Args:
        results: Reinforcement results
        skipped: Skipped elements
        errors: Errors encountered
        total_elements: Total input elements
    
    Returns:
        Statistics dictionary
    """
    # Total steel by type
    steel_by_type = {}
    for result in results:
        elem_type = result["type"]
        steel_kg = result["reinforcement"]["steel_kg"]
        steel_by_type[elem_type] = steel_by_type.get(elem_type, 0) + steel_kg
    
    # Total steel
    total_steel_kg = sum(r["reinforcement"]["steel_kg"] for r in results)
    
    # Average quality
    avg_quality = sum(r.get("quality_score", 0) for r in results) / len(results) if results else 0
    avg_confidence = sum(r.get("confidence", 0) for r in results) / len(results) if results else 0
    
    # Count by ratio source
    ratio_sources = {}
    for result in results:
        source = result["formula_trace"]["ratio_source"]
        ratio_sources[source] = ratio_sources.get(source, 0) + 1
    
    return {
        "total_elements": total_elements,
        "estimated_elements": len(results),
        "skipped_elements": len(skipped),
        "errors": len(errors),
        "success_rate": len(results) / total_elements if total_elements > 0 else 0,
        "total_steel_kg": round(total_steel_kg, 2),
        "steel_by_type": {k: round(v, 2) for k, v in steel_by_type.items()},
        "quality": {
            "average_quality_score": round(avg_quality, 3),
            "average_confidence": round(avg_confidence, 3)
        },
        "ratio_sources": ratio_sources
    }

def get_total_steel(reinforcement_result: Dict) -> float:
    """Get total steel quantity from reinforcement result
    
    Args:
        reinforcement_result: Output from estimate_reinforcement
    
    Returns:
        Total steel in kg
    """
    if not reinforcement_result.get("success"):
        return 0.0
    
    return reinforcement_result.get("statistics", {}).get("total_steel_kg", 0.0)

def get_steel_by_type(reinforcement_result: Dict, element_type: str) -> float:
    """Get steel quantity for specific element type
    
    Args:
        reinforcement_result: Output from estimate_reinforcement
        element_type: Type to filter
    
    Returns:
        Steel quantity in kg
    """
    if not reinforcement_result.get("success"):
        return 0.0
    
    steel_by_type = reinforcement_result.get("statistics", {}).get("steel_by_type", {})
    return steel_by_type.get(element_type, 0.0)

def get_reinforcement_by_element(reinforcement_result: Dict, element_id: str) -> Optional[Dict]:
    """Get reinforcement data for specific element
    
    Args:
        reinforcement_result: Output from estimate_reinforcement
        element_id: Element ID to find
    
    Returns:
        Reinforcement data or None
    """
    if not reinforcement_result.get("success"):
        return None
    
    estimations = reinforcement_result.get("reinforcement_estimation", [])
    
    for estimation in estimations:
        if estimation["element_id"] == element_id:
            return estimation
    
    return None
