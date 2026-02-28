"""Layer 4 Step C3: Material-Based Aggregation Engine"""
from typing import Dict, List, Optional
from collections import defaultdict
from app.ai.layer4_aggregation_key_builder import build_group_key, get_default_group_by_fields
from app.ai.layer4_work_category_mapper import resolve_work_category

def aggregate_materials(measurement_output: Dict,
                       reinforcement_output: Optional[Dict] = None,
                       group_by_fields: Optional[List[str]] = None,
                       work_category_map: Optional[Dict] = None) -> Dict:
    """Aggregate quantities by material and other dimensions
    
    Args:
        measurement_output: Output from Layer 4 Step 2 (measurements)
        reinforcement_output: Optional output from Layer 4 Step B (reinforcement)
        group_by_fields: Fields to group by (default: ["material"])
        work_category_map: Optional project-specific work category mapping
    
    Returns:
        Aggregated quantities by group
    """
    if not measurement_output.get("success"):
        return {
            "success": False,
            "error": "Input measurement failed",
            "aggregation": {},
            "summary": {}
        }
    
    # Use default grouping if not specified
    if not group_by_fields:
        group_by_fields = get_default_group_by_fields()
    
    # Initialize aggregation structure
    aggregation = defaultdict(lambda: {
        "quantities": defaultdict(float),
        "element_count": 0,
        "element_ids": []
    })
    
    # Build reinforcement lookup
    reinforcement_lookup = {}
    if reinforcement_output and reinforcement_output.get("success"):
        for r in reinforcement_output.get("reinforcement_estimation", []):
            reinforcement_lookup[r["element_id"]] = r
    
    # Process each element measurement
    elements = measurement_output.get("element_measurements", [])
    
    for element in elements:
        element_id = element.get("element_id", "unknown")
        element_type = element.get("type", "Unknown")
        material = element.get("material", "Unknown")
        measurements = element.get("measurements", {})
        
        # Build enriched element for grouping
        enriched_element = {
            "material": material,
            "type": element_type,
            "floor": element.get("floor", "Unknown"),
            "zone": element.get("zone", "Unknown")
        }
        
        # Build group key
        group_key = build_group_key(enriched_element, group_by_fields)
        
        # Resolve work category
        work_category = resolve_work_category(material, work_category_map)
        
        # Aggregate geometry-based quantities
        for metric_name, value in measurements.items():
            if isinstance(value, (int, float)):
                aggregation[group_key]["quantities"][metric_name] += value
        
        # Aggregate reinforcement if exists
        if element_id in reinforcement_lookup:
            steel_kg = reinforcement_lookup[element_id]["reinforcement"]["steel_kg"]
            aggregation[group_key]["quantities"]["steel_kg"] += steel_kg
        
        # Store metadata
        aggregation[group_key]["work_category"] = work_category
        aggregation[group_key]["element_count"] += 1
        aggregation[group_key]["element_ids"].append(element_id)
        
        # Store group dimensions
        for field in group_by_fields:
            aggregation[group_key][field] = enriched_element.get(field, "Unknown")
    
    # Convert to regular dict and round values
    final_aggregation = {}
    for group_key, data in aggregation.items():
        final_aggregation[group_key] = {
            **{k: v for k, v in data.items() if k != "quantities"},
            "quantities": {
                metric: round(value, 4) 
                for metric, value in data["quantities"].items()
            }
        }
    
    # Compute summary statistics
    summary = _compute_aggregation_summary(final_aggregation, group_by_fields)
    
    return {
        "success": True,
        "aggregation": final_aggregation,
        "summary": summary,
        "group_by_fields": group_by_fields
    }

def _compute_aggregation_summary(aggregation: Dict, group_by_fields: List[str]) -> Dict:
    """Compute summary statistics from aggregation
    
    Args:
        aggregation: Aggregated data
        group_by_fields: Fields used for grouping
    
    Returns:
        Summary statistics
    """
    total_groups = len(aggregation)
    total_elements = sum(data["element_count"] for data in aggregation.values())
    
    # Aggregate totals across all groups
    total_quantities = defaultdict(float)
    work_categories = set()
    
    for data in aggregation.values():
        for metric, value in data["quantities"].items():
            total_quantities[metric] += value
        
        work_categories.add(data.get("work_category", "Uncategorized"))
    
    # Round totals
    total_quantities = {k: round(v, 4) for k, v in total_quantities.items()}
    
    return {
        "total_groups": total_groups,
        "total_elements": total_elements,
        "total_quantities": dict(total_quantities),
        "work_categories": list(work_categories),
        "grouping_dimensions": group_by_fields
    }

def get_aggregation_by_work_category(aggregation_result: Dict) -> Dict:
    """Re-aggregate by work category
    
    Args:
        aggregation_result: Output from aggregate_materials
    
    Returns:
        Aggregation grouped by work category
    """
    if not aggregation_result.get("success"):
        return {}
    
    category_aggregation = defaultdict(lambda: defaultdict(float))
    
    for group_key, data in aggregation_result["aggregation"].items():
        category = data.get("work_category", "Uncategorized")
        
        for metric, value in data["quantities"].items():
            category_aggregation[category][metric] += value
    
    # Round values
    return {
        category: {metric: round(value, 4) for metric, value in quantities.items()}
        for category, quantities in category_aggregation.items()
    }

def get_total_by_metric(aggregation_result: Dict, metric_name: str) -> float:
    """Get total quantity for specific metric
    
    Args:
        aggregation_result: Output from aggregate_materials
        metric_name: Metric to sum (e.g., "volume", "steel_kg")
    
    Returns:
        Total quantity
    """
    if not aggregation_result.get("success"):
        return 0.0
    
    return aggregation_result.get("summary", {}).get("total_quantities", {}).get(metric_name, 0.0)

def filter_aggregation_by_material(aggregation_result: Dict, material: str) -> Dict:
    """Filter aggregation to specific material
    
    Args:
        aggregation_result: Output from aggregate_materials
        material: Material name to filter
    
    Returns:
        Filtered aggregation
    """
    if not aggregation_result.get("success"):
        return {}
    
    filtered = {}
    
    for group_key, data in aggregation_result["aggregation"].items():
        if data.get("material", "").lower() == material.lower():
            filtered[group_key] = data
    
    return filtered
