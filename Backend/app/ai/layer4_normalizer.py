"""Layer 4 Step 1B: Unit Normalization and Default Assignment"""
from typing import Dict, Optional

# Default values
DEFAULT_WALL_HEIGHT = 3.0  # meters
DEFAULT_COLUMN_HEIGHT = 3.0  # meters
DEFAULT_SLAB_THICKNESS = 0.15  # meters
DEFAULT_DOOR_WIDTH = 0.9  # meters
DEFAULT_DOOR_HEIGHT = 2.1  # meters
DEFAULT_WINDOW_WIDTH = 1.2  # meters
DEFAULT_WINDOW_HEIGHT = 1.5  # meters

def normalize_units(node: Dict) -> Dict:
    """Normalize all numeric fields to consistent units (meters)
    
    Args:
        node: Element node
    
    Returns:
        Node with normalized units
    """
    # Convert all numeric fields to float
    numeric_fields = ["length", "thickness", "height", "width", "depth", "area", "perimeter"]
    
    for field in numeric_fields:
        if field in node and node[field] is not None:
            try:
                node[field] = float(node[field])
            except (ValueError, TypeError):
                node[field] = 0.0
    
    return node

def assign_default_height(node: Dict, default_height: float = DEFAULT_WALL_HEIGHT) -> Dict:
    """Assign default height if missing
    
    Args:
        node: Element node
        default_height: Default height value
    
    Returns:
        Node with height assigned
    """
    node_type = node.get("type")
    
    # Walls
    if node_type == "Wall" and "height" not in node:
        node["height"] = default_height
        node["height_source"] = "default"
    
    # Columns
    elif node_type == "Column" and "height" not in node:
        node["height"] = DEFAULT_COLUMN_HEIGHT
        node["height_source"] = "default"
    
    return node

def assign_missing_dimensions(node: Dict) -> Dict:
    """Assign missing dimensions based on type defaults
    
    Args:
        node: Element node
    
    Returns:
        Node with dimensions filled
    """
    node_type = node.get("type")
    
    # Doors
    if node_type == "Door":
        if "width" not in node or node["width"] is None:
            node["width"] = DEFAULT_DOOR_WIDTH
            node["width_source"] = "default"
        if "height" not in node or node["height"] is None:
            node["height"] = DEFAULT_DOOR_HEIGHT
            node["height_source"] = "default"
    
    # Windows
    elif node_type == "Window":
        if "width" not in node or node["width"] is None:
            node["width"] = DEFAULT_WINDOW_WIDTH
            node["width_source"] = "default"
        if "height" not in node or node["height"] is None:
            node["height"] = DEFAULT_WINDOW_HEIGHT
            node["height_source"] = "default"
    
    # Slabs
    elif node_type == "Slab":
        if "thickness" not in node or node["thickness"] is None:
            node["thickness"] = DEFAULT_SLAB_THICKNESS
            node["thickness_source"] = "default"
    
    # Columns - compute area if missing
    elif node_type == "Column":
        if "area" not in node or node["area"] is None:
            if "width" in node and "depth" in node:
                node["area"] = node["width"] * node["depth"]
                node["area_source"] = "computed"
    
    return node

def normalize_material(node: Dict) -> Dict:
    """Normalize material names to standard format
    
    Args:
        node: Element node
    
    Returns:
        Node with normalized material
    """
    if "material" not in node or not node["material"]:
        # Assign default materials by type
        defaults = {
            "Wall": "Brick",
            "Slab": "Concrete",
            "Column": "RCC",
            "Door": "Wood",
            "Window": "Aluminum"
        }
        node["material"] = defaults.get(node.get("type"), "Unknown")
        node["material_source"] = "default"
    else:
        # Capitalize first letter
        node["material"] = node["material"].strip().title()
    
    return node

def normalize_node(node: Dict, default_height: float = DEFAULT_WALL_HEIGHT) -> Dict:
    """Apply all normalizations to a node
    
    Args:
        node: Element node
        default_height: Default height for walls/columns
    
    Returns:
        Fully normalized node
    """
    node = normalize_units(node)
    node = assign_default_height(node, default_height)
    node = assign_missing_dimensions(node)
    node = normalize_material(node)
    
    return node
