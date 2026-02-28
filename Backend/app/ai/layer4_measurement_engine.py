"""Layer 4 Step 2C: Measurement Engine (Executor)"""
from typing import Dict, List
from app.ai.layer4_measurement_registry import (
    get_primary_strategy,
    get_secondary_strategies,
    get_supported_element_types
)

def compute_element_measurements(processed_graph: Dict, 
                                 include_secondary: bool = False) -> Dict:
    """Compute measurements for all elements using registered strategies
    
    Args:
        processed_graph: Output from Layer 4 Step 1
        include_secondary: Include secondary measurements (plaster, paint, etc.)
    
    Returns:
        Measurement results with statistics
    """
    if not processed_graph.get("success"):
        return {
            "success": False,
            "error": "Input graph processing failed",
            "element_measurements": [],
            "skipped": []
        }
    
    elements = processed_graph.get("elements", [])
    
    primary_results = []
    secondary_results = []
    skipped = []
    errors = []
    
    # Process each element
    for element in elements:
        element_id = element.get("id", "unknown")
        element_type = element.get("type", "unknown")
        
        # Skip non-measurable elements
        if not element.get("is_measurable", True):
            skipped.append({
                "element_id": element_id,
                "type": element_type,
                "reason": "not_measurable"
            })
            continue
        
        # Get primary strategy
        strategy = get_primary_strategy(element_type)
        
        if not strategy:
            skipped.append({
                "element_id": element_id,
                "type": element_type,
                "reason": "no_strategy_registered"
            })
            continue
        
        # Execute primary measurement
        try:
            measurement = strategy(element)
            
            if measurement:
                # Add quality metadata
                measurement["quality_score"] = element.get("quality_score", 0.5)
                measurement["confidence"] = element.get("confidence", 0.5)
                measurement["has_defaults"] = element.get("has_defaults", False)
                
                primary_results.append(measurement)
            else:
                skipped.append({
                    "element_id": element_id,
                    "type": element_type,
                    "reason": "calculation_returned_none"
                })
        
        except Exception as e:
            errors.append({
                "element_id": element_id,
                "type": element_type,
                "error": str(e)
            })
        
        # Execute secondary measurements if enabled
        if include_secondary:
            secondary_strategies = get_secondary_strategies(element_type, enabled_only=True)
            
            for sec_strategy in secondary_strategies:
                try:
                    func = sec_strategy["function"]
                    params = sec_strategy.get("params", {})
                    
                    sec_measurement = func(element, **params)
                    
                    if sec_measurement:
                        sec_measurement["quality_score"] = element.get("quality_score", 0.5)
                        sec_measurement["confidence"] = element.get("confidence", 0.5)
                        secondary_results.append(sec_measurement)
                
                except Exception as e:
                    errors.append({
                        "element_id": element_id,
                        "type": element_type,
                        "measurement_type": sec_strategy["name"],
                        "error": str(e)
                    })
    
    # Compute statistics
    statistics = _compute_measurement_statistics(primary_results, secondary_results, 
                                                 skipped, errors, len(elements))
    
    return {
        "success": True,
        "element_measurements": primary_results,
        "secondary_measurements": secondary_results if include_secondary else [],
        "skipped": skipped,
        "errors": errors,
        "statistics": statistics
    }

def _compute_measurement_statistics(primary: List[Dict], secondary: List[Dict],
                                    skipped: List[Dict], errors: List[Dict],
                                    total_elements: int) -> Dict:
    """Compute measurement statistics
    
    Args:
        primary: Primary measurements
        secondary: Secondary measurements
        skipped: Skipped elements
        errors: Errors encountered
        total_elements: Total input elements
    
    Returns:
        Statistics dictionary
    """
    # Count by type
    type_counts = {}
    for measurement in primary:
        elem_type = measurement["type"]
        type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
    
    # Total volumes and areas
    total_volume = sum(
        m["measurements"].get("volume", 0) 
        for m in primary 
        if "volume" in m["measurements"]
    )
    
    total_area = sum(
        m["measurements"].get("area", 0) 
        for m in primary 
        if "area" in m["measurements"]
    )
    
    total_count = sum(
        m["measurements"].get("count", 0) 
        for m in primary 
        if "count" in m["measurements"]
    )
    
    # Quality metrics
    avg_quality = sum(m.get("quality_score", 0) for m in primary) / len(primary) if primary else 0
    avg_confidence = sum(m.get("confidence", 0) for m in primary) / len(primary) if primary else 0
    
    with_defaults = sum(1 for m in primary if m.get("has_defaults", False))
    
    return {
        "total_elements": total_elements,
        "measured_elements": len(primary),
        "skipped_elements": len(skipped),
        "errors": len(errors),
        "success_rate": len(primary) / total_elements if total_elements > 0 else 0,
        "by_type": type_counts,
        "totals": {
            "volume_m3": round(total_volume, 4),
            "area_m2": round(total_area, 4),
            "count": total_count
        },
        "quality": {
            "average_quality_score": round(avg_quality, 3),
            "average_confidence": round(avg_confidence, 3),
            "elements_with_defaults": with_defaults
        },
        "secondary_measurements": len(secondary)
    }

def get_measurements_by_type(measurement_result: Dict, element_type: str) -> List[Dict]:
    """Filter measurements by element type
    
    Args:
        measurement_result: Output from compute_element_measurements
        element_type: Type to filter
    
    Returns:
        List of measurements for specified type
    """
    if not measurement_result.get("success"):
        return []
    
    measurements = measurement_result.get("element_measurements", [])
    return [m for m in measurements if m["type"] == element_type]

def get_total_volume(measurement_result: Dict) -> float:
    """Get total volume from all measurements
    
    Args:
        measurement_result: Output from compute_element_measurements
    
    Returns:
        Total volume in m³
    """
    if not measurement_result.get("success"):
        return 0.0
    
    return measurement_result.get("statistics", {}).get("totals", {}).get("volume_m3", 0.0)

def get_total_area(measurement_result: Dict) -> float:
    """Get total area from all measurements
    
    Args:
        measurement_result: Output from compute_element_measurements
    
    Returns:
        Total area in m²
    """
    if not measurement_result.get("success"):
        return 0.0
    
    return measurement_result.get("statistics", {}).get("totals", {}).get("area_m2", 0.0)
