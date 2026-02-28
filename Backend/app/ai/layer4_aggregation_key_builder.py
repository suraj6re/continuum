"""Layer 4 Step C2: Aggregation Key Builder (Dynamic Grouping)"""
from typing import Dict, List

def build_group_key(element: Dict, group_by_fields: List[str]) -> str:
    """Build aggregation key from element fields dynamically
    
    Args:
        element: Element dict with fields
        group_by_fields: List of field names to group by (e.g., ["material", "type"])
    
    Returns:
        Aggregation key string (e.g., "Concrete_Slab")
    """
    key_parts = []
    
    for field in group_by_fields:
        value = element.get(field)
        
        # Handle missing values
        if value is None or value == "":
            value = "Unknown"
        
        # Normalize value
        key_parts.append(str(value).strip())
    
    return "_".join(key_parts)

def parse_group_key(group_key: str, group_by_fields: List[str]) -> Dict:
    """Parse aggregation key back into field values
    
    Args:
        group_key: Aggregation key (e.g., "Concrete_Slab")
        group_by_fields: List of field names used for grouping
    
    Returns:
        Dict mapping field names to values
    """
    parts = group_key.split("_")
    
    result = {}
    for i, field in enumerate(group_by_fields):
        if i < len(parts):
            result[field] = parts[i]
        else:
            result[field] = "Unknown"
    
    return result

def get_default_group_by_fields() -> List[str]:
    """Get default grouping fields
    
    Returns:
        List of default field names
    """
    return ["material"]

def validate_group_by_fields(fields: List[str]) -> bool:
    """Validate grouping fields
    
    Args:
        fields: List of field names
    
    Returns:
        True if valid
    """
    if not fields or not isinstance(fields, list):
        return False
    
    # Check for valid field names
    valid_fields = {"material", "type", "floor", "work_category", "zone"}
    
    for field in fields:
        if field not in valid_fields:
            return False
    
    return True
