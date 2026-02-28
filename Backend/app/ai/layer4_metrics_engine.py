"""Layer 4 Step E: Validation Metrics Engine"""
from typing import Dict, List, Optional
from app.ai.layer4_metrics_registry import get_default_metric_rules, MetricRule

def compute_validation_metrics(measurement_output: Dict,
                               reinforcement_output: Optional[Dict] = None,
                               custom_rules: Optional[List[MetricRule]] = None) -> Dict:
    """Compute validation metrics using rule-based extraction
    
    Args:
        measurement_output: Output from Layer 4 Step 2
        reinforcement_output: Optional output from Layer 4 Step B
        custom_rules: Optional custom metric rules
    
    Returns:
        Validation metrics dictionary
    """
    if not measurement_output.get("success"):
        return {
            "success": False,
            "error": "Input measurement failed",
            "metrics": {}
        }
    
    # Get metric rules
    rules = custom_rules if custom_rules else get_default_metric_rules()
    
    # Build enriched elements list
    elements = _build_enriched_elements(measurement_output, reinforcement_output)
    
    # Execute each rule
    metrics = {}
    metric_details = {}
    
    for rule in rules:
        total_value = 0.0
        contributing_elements = []
        
        for element in elements:
            try:
                # Apply filter
                if rule.filter_fn(element):
                    # Compute contribution
                    contribution = rule.compute_fn(element)
                    
                    if contribution and contribution > 0:
                        total_value += contribution
                        contributing_elements.append({
                            "element_id": element.get("element_id"),
                            "type": element.get("type"),
                            "contribution": round(contribution, 4)
                        })
            except Exception:
                # Skip elements that cause errors
                continue
        
        # Store metric
        metrics[rule.name] = round(total_value, 4)
        metric_details[rule.name] = {
            "value": round(total_value, 4),
            "description": rule.description,
            "contributing_elements_count": len(contributing_elements),
            "contributing_elements": contributing_elements[:10]  # Limit to first 10
        }
    
    # Compute summary statistics
    summary = _compute_metrics_summary(metrics, elements)
    
    return {
        "success": True,
        "metrics": metrics,
        "metric_details": metric_details,
        "summary": summary
    }

def _build_enriched_elements(measurement_output: Dict,
                             reinforcement_output: Optional[Dict]) -> List[Dict]:
    """Build enriched elements list with measurements and reinforcement
    
    Args:
        measurement_output: Measurement results
        reinforcement_output: Optional reinforcement results
    
    Returns:
        List of enriched element dicts
    """
    enriched = []
    
    # Build reinforcement lookup
    reinforcement_lookup = {}
    if reinforcement_output and reinforcement_output.get("success"):
        for r in reinforcement_output.get("reinforcement_estimation", []):
            reinforcement_lookup[r["element_id"]] = r["reinforcement"]["steel_kg"]
    
    # Enrich each element
    for element in measurement_output.get("element_measurements", []):
        enriched_element = {
            "element_id": element.get("element_id"),
            "type": element.get("type"),
            "material": element.get("material", "Unknown"),
            "measurements": element.get("measurements", {}).copy(),
            "confidence": element.get("confidence"),
            "quality_score": element.get("quality_score")
        }
        
        # Add steel if available
        element_id = element.get("element_id")
        if element_id in reinforcement_lookup:
            enriched_element["measurements"]["steel_kg"] = reinforcement_lookup[element_id]
        
        enriched.append(enriched_element)
    
    return enriched

def _compute_metrics_summary(metrics: Dict, elements: List[Dict]) -> Dict:
    """Compute summary statistics for metrics
    
    Args:
        metrics: Computed metrics
        elements: Element list
    
    Returns:
        Summary statistics
    """
    # Count elements by type
    type_counts = {}
    for element in elements:
        elem_type = element.get("type", "Unknown")
        type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
    
    # Identify key metrics
    key_metrics = {
        "structural": {
            "concrete_volume_m3": metrics.get("total_concrete_volume", 0),
            "steel_weight_kg": metrics.get("total_steel_weight", 0),
            "slab_area_m2": metrics.get("total_slab_area", 0)
        },
        "masonry": {
            "masonry_volume_m3": metrics.get("total_masonry_volume", 0),
            "wall_length_m": metrics.get("total_wall_length", 0)
        },
        "openings": {
            "door_count": int(metrics.get("total_door_count", 0)),
            "window_count": int(metrics.get("total_window_count", 0))
        }
    }
    
    return {
        "total_elements": len(elements),
        "element_type_counts": type_counts,
        "key_metrics": key_metrics,
        "total_metrics_computed": len(metrics)
    }

def get_metric_value(metrics_result: Dict, metric_name: str) -> float:
    """Get specific metric value
    
    Args:
        metrics_result: Output from compute_validation_metrics
        metric_name: Metric name
    
    Returns:
        Metric value or 0.0
    """
    if not metrics_result.get("success"):
        return 0.0
    
    return metrics_result.get("metrics", {}).get(metric_name, 0.0)

def get_contributing_elements(metrics_result: Dict, metric_name: str) -> List[Dict]:
    """Get elements contributing to specific metric
    
    Args:
        metrics_result: Output from compute_validation_metrics
        metric_name: Metric name
    
    Returns:
        List of contributing elements
    """
    if not metrics_result.get("success"):
        return []
    
    details = metrics_result.get("metric_details", {}).get(metric_name, {})
    return details.get("contributing_elements", [])

def export_metrics_for_layer5(metrics_result: Dict) -> Dict:
    """Export metrics in format ready for Layer 5 validation
    
    Args:
        metrics_result: Output from compute_validation_metrics
    
    Returns:
        Layer 5 ready metrics
    """
    if not metrics_result.get("success"):
        return {}
    
    metrics = metrics_result.get("metrics", {})
    summary = metrics_result.get("summary", {})
    
    return {
        "validation_hooks": {
            "total_slab_area": metrics.get("total_slab_area", 0),
            "total_concrete_volume": metrics.get("total_concrete_volume", 0),
            "total_wall_length": metrics.get("total_wall_length", 0),
            "total_steel_weight": metrics.get("total_steel_weight", 0),
            "total_masonry_volume": metrics.get("total_masonry_volume", 0),
            "element_counts": summary.get("element_type_counts", {})
        },
        "metadata": {
            "total_elements": summary.get("total_elements", 0),
            "metrics_computed": summary.get("total_metrics_computed", 0)
        }
    }
