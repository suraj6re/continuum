"""Layer 4 Step 1A: Graph Validation"""
from typing import Dict, Tuple, Optional

# Required fields per element type
REQUIRED_FIELDS = {
    "Wall": ["length", "thickness"],
    "Slab": ["area"],
    "Column": ["area"],  # OR width+depth checked separately
    "Door": ["width", "height"],
    "Window": ["width", "height"]
}

def validate_node(node: Dict) -> Tuple[bool, Optional[str]]:
    """Validate node has required fields
    
    Args:
        node: Element node from Layer 3
    
    Returns:
        (is_valid, error_message)
    """
    # Check type exists
    if "type" not in node:
        return False, "Missing 'type' field"
    
    node_type = node["type"]
    
    # Check supported type
    if node_type not in REQUIRED_FIELDS:
        return False, f"Unsupported type: {node_type}"
    
    # Special case: Column can have area OR (width + depth)
    if node_type == "Column":
        has_area = "area" in node
        has_dimensions = "width" in node and "depth" in node
        
        if not (has_area or has_dimensions):
            return False, "Column missing 'area' or 'width'+'depth'"
        
        return True, None
    
    # Check required fields
    required = REQUIRED_FIELDS[node_type]
    for field in required:
        if field not in node or node[field] is None:
            return False, f"Missing required field: {field}"
    
    return True, None

def validate_graph(graph: Dict) -> Dict:
    """Validate entire graph structure
    
    Args:
        graph: Layer 3 output with elements and relationships
    
    Returns:
        Validation report with errors
    """
    errors = []
    warnings = []
    
    # Check graph structure
    if "elements" not in graph:
        return {
            "valid": False,
            "errors": ["Missing 'elements' key in graph"],
            "warnings": []
        }
    
    elements = graph.get("elements", [])
    
    if not elements:
        warnings.append("No elements found in graph")
    
    # Validate each element
    for i, element in enumerate(elements):
        valid, error = validate_node(element)
        
        if not valid:
            errors.append({
                "index": i,
                "id": element.get("id", "unknown"),
                "type": element.get("type", "unknown"),
                "error": error
            })
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "total_elements": len(elements),
        "valid_elements": len(elements) - len(errors)
    }
