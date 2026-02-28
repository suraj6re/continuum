"""Layer 4 Step E: Validation Metrics Registry (Rule-Based Architecture)"""
from typing import Dict, List, Callable, Any

class MetricRule:
    """Metric extraction rule with filter and compute functions"""
    
    def __init__(self, name: str, filter_fn: Callable, compute_fn: Callable, 
                 description: str = ""):
        """Initialize metric rule
        
        Args:
            name: Metric name (e.g., "total_slab_area")
            filter_fn: Function to filter elements (returns bool)
            compute_fn: Function to compute contribution (returns number)
            description: Human-readable description
        """
        self.name = name
        self.filter_fn = filter_fn
        self.compute_fn = compute_fn
        self.description = description

def get_default_metric_rules() -> List[MetricRule]:
    """Get default validation metric rules
    
    Returns:
        List of MetricRule objects
    """
    return [
        MetricRule(
            name="total_slab_area",
            filter_fn=lambda e: e.get("type") == "Slab",
            compute_fn=lambda e: e.get("measurements", {}).get("area", 0),
            description="Total area of all slabs"
        ),
        
        MetricRule(
            name="total_concrete_volume",
            filter_fn=lambda e: _is_concrete_material(e.get("material", "")),
            compute_fn=lambda e: e.get("measurements", {}).get("volume", 0),
            description="Total volume of concrete elements"
        ),
        
        MetricRule(
            name="total_wall_length",
            filter_fn=lambda e: e.get("type") == "Wall",
            compute_fn=lambda e: e.get("measurements", {}).get("length", 0),
            description="Total length of all walls"
        ),
        
        MetricRule(
            name="total_steel_weight",
            filter_fn=lambda e: "steel_kg" in e.get("measurements", {}),
            compute_fn=lambda e: e.get("measurements", {}).get("steel_kg", 0),
            description="Total weight of reinforcement steel"
        ),
        
        MetricRule(
            name="total_column_count",
            filter_fn=lambda e: e.get("type") == "Column",
            compute_fn=lambda e: 1,
            description="Total number of columns"
        ),
        
        MetricRule(
            name="total_door_count",
            filter_fn=lambda e: e.get("type") == "Door",
            compute_fn=lambda e: e.get("measurements", {}).get("count", 1),
            description="Total number of doors"
        ),
        
        MetricRule(
            name="total_window_count",
            filter_fn=lambda e: e.get("type") == "Window",
            compute_fn=lambda e: e.get("measurements", {}).get("count", 1),
            description="Total number of windows"
        ),
        
        MetricRule(
            name="total_masonry_volume",
            filter_fn=lambda e: _is_masonry_material(e.get("material", "")),
            compute_fn=lambda e: e.get("measurements", {}).get("volume", 0),
            description="Total volume of masonry elements"
        )
    ]

def _is_concrete_material(material: str) -> bool:
    """Check if material is concrete-based
    
    Args:
        material: Material name
    
    Returns:
        True if concrete
    """
    material_lower = material.lower()
    concrete_keywords = ["concrete", "rcc", "cement"]
    return any(keyword in material_lower for keyword in concrete_keywords)

def _is_masonry_material(material: str) -> bool:
    """Check if material is masonry-based
    
    Args:
        material: Material name
    
    Returns:
        True if masonry
    """
    material_lower = material.lower()
    masonry_keywords = ["brick", "block", "stone", "masonry"]
    return any(keyword in material_lower for keyword in masonry_keywords)

def add_custom_metric_rule(rules: List[MetricRule], name: str, 
                           filter_fn: Callable, compute_fn: Callable,
                           description: str = "") -> List[MetricRule]:
    """Add custom metric rule (extensibility)
    
    Args:
        rules: Existing rules list
        name: Metric name
        filter_fn: Filter function
        compute_fn: Compute function
        description: Description
    
    Returns:
        Updated rules list
    """
    new_rule = MetricRule(name, filter_fn, compute_fn, description)
    rules.append(new_rule)
    return rules

def get_metric_rule_by_name(rules: List[MetricRule], name: str) -> MetricRule:
    """Get specific metric rule by name
    
    Args:
        rules: Rules list
        name: Metric name
    
    Returns:
        MetricRule or None
    """
    for rule in rules:
        if rule.name == name:
            return rule
    return None
