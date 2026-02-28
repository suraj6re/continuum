"""Layer 4 Step C1: Work Category Mapper (Configurable Mapping)"""
from typing import Dict, Optional

# Default work category mapping (configurable per project)
DEFAULT_WORK_CATEGORY_MAP = {
    "Concrete": "Structural",
    "RCC": "Structural",
    "Brick": "Masonry",
    "Brickwork": "Masonry",
    "Steel": "Reinforcement",
    "Wood": "Carpentry",
    "Aluminum": "Metalwork",
    "Glass": "Glazing",
    "Plaster": "Finishing",
    "Paint": "Finishing",
    "Tile": "Finishing"
}

def resolve_work_category(material: str, project_map: Optional[Dict] = None) -> str:
    """Resolve work category from material name using partial matching
    
    Args:
        material: Material name (e.g., "Concrete", "Brick")
        project_map: Optional project-specific category mapping
    
    Returns:
        Work category name
    """
    if not material:
        return "Uncategorized"
    
    # Use project map if provided, otherwise use defaults
    mapping = project_map or DEFAULT_WORK_CATEGORY_MAP
    
    material_lower = material.lower()
    
    # Try exact match first
    for key, category in mapping.items():
        if key.lower() == material_lower:
            return category
    
    # Try partial match (e.g., "RCC Concrete" matches "Concrete")
    for key, category in mapping.items():
        if key.lower() in material_lower:
            return category
    
    return "Uncategorized"

def get_all_work_categories(project_map: Optional[Dict] = None) -> set:
    """Get set of all work categories
    
    Args:
        project_map: Optional project-specific mapping
    
    Returns:
        Set of category names
    """
    mapping = project_map or DEFAULT_WORK_CATEGORY_MAP
    return set(mapping.values())

def add_work_category_mapping(material: str, category: str, 
                               project_map: Optional[Dict] = None) -> Dict:
    """Add new material-to-category mapping (extensibility)
    
    Args:
        material: Material name
        category: Work category
        project_map: Existing project map or None
    
    Returns:
        Updated project map
    """
    if project_map is None:
        project_map = DEFAULT_WORK_CATEGORY_MAP.copy()
    
    project_map[material] = category
    return project_map
