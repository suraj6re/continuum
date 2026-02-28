"""Layer 4 Step 2A: Measurement Strategies (Strategy Pattern)"""
from typing import Dict, Optional

def calculate_wall(node: Dict) -> Optional[Dict]:
    """Calculate wall measurements
    
    Formula: volume = length × thickness × height
    
    Args:
        node: Wall element with dimensions
    
    Returns:
        Measurement result or None if missing data
    """
    length = node.get("length")
    thickness = node.get("thickness")
    height = node.get("height")
    
    # Validate all required dimensions exist
    if not all([length, thickness, height]):
        return None
    
    # Validate positive values
    if any(v <= 0 for v in [length, thickness, height]):
        return None
    
    # Calculate volume
    volume = length * thickness * height
    
    # Build traceability
    dimension_sources = {
        "length": node.get("length_source", "geometry"),
        "thickness": node.get("thickness_source", "geometry"),
        "height": node.get("height_source", "geometry")
    }
    
    return {
        "element_id": node["id"],
        "type": "Wall",
        "measurements": {
            "volume": round(volume, 4),
            "length": round(length, 3),
            "thickness": round(thickness, 3),
            "height": round(height, 3)
        },
        "unit": "m³",
        "formula": "length × thickness × height",
        "formula_trace": {
            "formula": "Wall Volume = L × T × H",
            "calculation": f"{length:.3f} × {thickness:.3f} × {height:.3f} = {volume:.4f} m³",
            "dimension_sources": dimension_sources,
            "has_defaults": node.get("has_defaults", False)
        }
    }

def calculate_slab(node: Dict) -> Optional[Dict]:
    """Calculate slab measurements
    
    Formula: volume = area × thickness
    
    Args:
        node: Slab element with dimensions
    
    Returns:
        Measurement result or None if missing data
    """
    area = node.get("area")
    thickness = node.get("thickness")
    
    if not all([area, thickness]):
        return None
    
    if any(v <= 0 for v in [area, thickness]):
        return None
    
    volume = area * thickness
    
    # Build traceability
    dimension_sources = {
        "area": node.get("area_source", "geometry"),
        "thickness": node.get("thickness_source", "geometry")
    }
    
    return {
        "element_id": node["id"],
        "type": "Slab",
        "measurements": {
            "volume": round(volume, 4),
            "area": round(area, 3),
            "thickness": round(thickness, 3)
        },
        "unit": "m³",
        "formula": "area × thickness",
        "formula_trace": {
            "formula": "Slab Volume = A × T",
            "calculation": f"{area:.3f} × {thickness:.3f} = {volume:.4f} m³",
            "dimension_sources": dimension_sources,
            "has_defaults": node.get("has_defaults", False)
        }
    }

def calculate_column(node: Dict) -> Optional[Dict]:
    """Calculate column measurements
    
    Formula: volume = width × depth × height
    OR: volume = area × height (if area provided)
    
    Args:
        node: Column element with dimensions
    
    Returns:
        Measurement result or None if missing data
    """
    height = node.get("height")
    
    if not height or height <= 0:
        return None
    
    # Method 1: Use area if available
    area = node.get("area")
    if area and area > 0:
        volume = area * height
        
        dimension_sources = {
            "area": node.get("area_source", "geometry"),
            "height": node.get("height_source", "geometry")
        }
        
        return {
            "element_id": node["id"],
            "type": "Column",
            "measurements": {
                "volume": round(volume, 4),
                "area": round(area, 4),
                "height": round(height, 3)
            },
            "unit": "m³",
            "formula": "area × height",
            "formula_trace": {
                "formula": "Column Volume = A × H",
                "calculation": f"{area:.4f} × {height:.3f} = {volume:.4f} m³",
                "dimension_sources": dimension_sources,
                "has_defaults": node.get("has_defaults", False)
            }
        }
    
    # Method 2: Calculate from width × depth
    width = node.get("width")
    depth = node.get("depth")
    
    if not all([width, depth]):
        return None
    
    if any(v <= 0 for v in [width, depth]):
        return None
    
    area = width * depth
    volume = area * height
    
    dimension_sources = {
        "width": node.get("width_source", "geometry"),
        "depth": node.get("depth_source", "geometry"),
        "height": node.get("height_source", "geometry")
    }
    
    return {
        "element_id": node["id"],
        "type": "Column",
        "measurements": {
            "volume": round(volume, 4),
            "width": round(width, 3),
            "depth": round(depth, 3),
            "height": round(height, 3),
            "area": round(area, 4)
        },
        "unit": "m³",
        "formula": "width × depth × height",
        "formula_trace": {
            "formula": "Column Volume = W × D × H",
            "calculation": f"{width:.3f} × {depth:.3f} × {height:.3f} = {volume:.4f} m³",
            "dimension_sources": dimension_sources,
            "has_defaults": node.get("has_defaults", False)
        }
    }

def calculate_opening(node: Dict) -> Optional[Dict]:
    """Calculate door/window measurements
    
    Formula: area = width × height, count = 1
    
    Args:
        node: Door or Window element with dimensions
    
    Returns:
        Measurement result or None if missing data
    """
    width = node.get("width")
    height = node.get("height")
    
    if not all([width, height]):
        return None
    
    if any(v <= 0 for v in [width, height]):
        return None
    
    area = width * height
    
    return {
        "element_id": node["id"],
        "type": node["type"],
        "measurements": {
            "count": 1,
            "area": round(area, 4),
            "width": round(width, 3),
            "height": round(height, 3)
        },
        "unit": "m²",
        "formula": "width × height"
    }

def calculate_wall_plaster(node: Dict, both_sides: bool = True) -> Optional[Dict]:
    """Calculate wall plaster area (secondary measurement)
    
    Formula: area = 2 × length × height (both sides)
    OR: area = length × height (one side)
    
    Args:
        node: Wall element
        both_sides: Calculate for both sides (default True)
    
    Returns:
        Plaster measurement or None if missing data
    """
    length = node.get("length")
    height = node.get("height")
    
    if not all([length, height]):
        return None
    
    if any(v <= 0 for v in [length, height]):
        return None
    
    # Calculate area
    multiplier = 2 if both_sides else 1
    area = multiplier * length * height
    
    return {
        "element_id": node["id"],
        "type": "Wall",
        "measurement_type": "plaster",
        "measurements": {
            "plaster_area": round(area, 4),
            "sides": 2 if both_sides else 1
        },
        "unit": "m²",
        "formula": f"{'2 × ' if both_sides else ''}length × height"
    }

def calculate_wall_paint(node: Dict, both_sides: bool = True) -> Optional[Dict]:
    """Calculate wall paint area (secondary measurement)
    
    Same as plaster but tracked separately
    
    Args:
        node: Wall element
        both_sides: Calculate for both sides (default True)
    
    Returns:
        Paint measurement or None if missing data
    """
    result = calculate_wall_plaster(node, both_sides)
    
    if result:
        result["measurement_type"] = "paint"
        result["measurements"]["paint_area"] = result["measurements"].pop("plaster_area")
    
    return result
