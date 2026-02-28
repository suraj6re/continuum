"""Layer 4 Step B2: Reinforcement Registry (Eligibility Rules)"""
from typing import Dict, Set

# Element types that typically contain concrete and require reinforcement
CONCRETE_ELEMENT_TYPES: Set[str] = {
    "Slab",
    "Column",
    "Beam",
    "Wall",  # RCC walls only
    "Footing",
    "Foundation"
}

# Material keywords that indicate concrete
CONCRETE_MATERIAL_KEYWORDS: Set[str] = {
    "concrete",
    "rcc",
    "reinforced",
    "cement"
}

def is_concrete_element(element: Dict) -> bool:
    """Check if element is eligible for reinforcement estimation
    
    Eligibility criteria:
    1. Element type is in concrete types list
    2. OR material contains concrete keywords
    
    Args:
        element: Element dict with type and material
    
    Returns:
        True if eligible for reinforcement
    """
    element_type = element.get("type", "")
    material = element.get("material", "").lower()
    
    # Check by type
    if element_type in CONCRETE_ELEMENT_TYPES:
        return True
    
    # Check by material keywords
    if any(keyword in material for keyword in CONCRETE_MATERIAL_KEYWORDS):
        return True
    
    return False

def has_volume_measurement(element: Dict) -> bool:
    """Check if element has volume measurement
    
    Args:
        element: Element measurement dict
    
    Returns:
        True if has volume
    """
    measurements = element.get("measurements", {})
    volume = measurements.get("volume")
    
    return volume is not None and volume > 0

def is_eligible_for_reinforcement(element: Dict) -> tuple[bool, str]:
    """Check if element is eligible for reinforcement estimation
    
    Args:
        element: Element measurement dict
    
    Returns:
        (is_eligible, reason)
    """
    # Check if concrete element
    if not is_concrete_element(element):
        return False, "not_concrete_element"
    
    # Check if has volume
    if not has_volume_measurement(element):
        return False, "no_volume_measurement"
    
    return True, "eligible"

def get_concrete_element_types() -> Set[str]:
    """Get set of concrete element types
    
    Returns:
        Set of element type names
    """
    return CONCRETE_ELEMENT_TYPES.copy()

def add_concrete_element_type(element_type: str) -> None:
    """Add new element type to concrete registry (extensibility)
    
    Args:
        element_type: Type to add
    """
    CONCRETE_ELEMENT_TYPES.add(element_type)
