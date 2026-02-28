"""Layer 4 Step D1: Confidence Weight Resolver (Dynamic Metric Selection)"""
from typing import Dict, Optional, List

# Priority order for metrics (configurable)
# Higher priority metrics are used first for confidence weighting
PRIORITY_METRICS = ["volume", "area", "steel_kg", "count"]

def resolve_primary_metric(aggregated_item: Dict) -> Optional[str]:
    """Resolve which metric to use for confidence weighting
    
    Uses priority order: volume > area > steel_kg > count
    Selects first metric that exists and has positive value
    
    Args:
        aggregated_item: Aggregated quantities dict
    
    Returns:
        Primary metric name or None
    """
    quantities = aggregated_item.get("quantities", {})
    
    for metric in PRIORITY_METRICS:
        if metric in quantities and quantities[metric] > 0:
            return metric
    
    return None

def get_metric_priority_order() -> List[str]:
    """Get current metric priority order
    
    Returns:
        List of metric names in priority order
    """
    return PRIORITY_METRICS.copy()

def set_metric_priority_order(priority_list: List[str]) -> None:
    """Set custom metric priority order (extensibility)
    
    Args:
        priority_list: New priority order
    """
    global PRIORITY_METRICS
    PRIORITY_METRICS = priority_list

def is_valid_metric(metric_name: str) -> bool:
    """Check if metric is valid for confidence weighting
    
    Args:
        metric_name: Metric to check
    
    Returns:
        True if valid
    """
    return metric_name in PRIORITY_METRICS
