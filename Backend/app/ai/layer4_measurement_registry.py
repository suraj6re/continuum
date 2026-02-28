"""Layer 4 Step 2B: Measurement Registry (Strategy Registry)"""
from typing import Dict, Callable, List
from app.ai.layer4_measurement_strategies import (
    calculate_wall,
    calculate_slab,
    calculate_column,
    calculate_opening,
    calculate_wall_plaster,
    calculate_wall_paint
)

# Primary measurement registry - maps element type to calculation function
MEASUREMENT_REGISTRY: Dict[str, Callable] = {
    "Wall": calculate_wall,
    "Slab": calculate_slab,
    "Column": calculate_column,
    "Door": calculate_opening,
    "Window": calculate_opening
}

# Secondary measurement registry - additional measurements per element type
# These are optional and can be enabled based on project requirements
SECONDARY_MEASUREMENTS: Dict[str, List[Dict]] = {
    "Wall": [
        {
            "name": "plaster",
            "function": calculate_wall_plaster,
            "enabled": False,  # Enable based on project config
            "params": {"both_sides": True}
        },
        {
            "name": "paint",
            "function": calculate_wall_paint,
            "enabled": False,
            "params": {"both_sides": True}
        }
    ]
}

def get_primary_strategy(element_type: str) -> Callable:
    """Get primary measurement strategy for element type
    
    Args:
        element_type: Type of element (Wall, Slab, etc.)
    
    Returns:
        Calculation function or None if not registered
    """
    return MEASUREMENT_REGISTRY.get(element_type)

def get_secondary_strategies(element_type: str, enabled_only: bool = True) -> List[Dict]:
    """Get secondary measurement strategies for element type
    
    Args:
        element_type: Type of element
        enabled_only: Return only enabled strategies
    
    Returns:
        List of secondary measurement configs
    """
    strategies = SECONDARY_MEASUREMENTS.get(element_type, [])
    
    if enabled_only:
        return [s for s in strategies if s.get("enabled", False)]
    
    return strategies

def register_measurement_strategy(element_type: str, strategy_function: Callable) -> None:
    """Register a new measurement strategy (extensibility)
    
    Args:
        element_type: Type of element
        strategy_function: Calculation function
    """
    MEASUREMENT_REGISTRY[element_type] = strategy_function

def enable_secondary_measurement(element_type: str, measurement_name: str) -> bool:
    """Enable a secondary measurement for an element type
    
    Args:
        element_type: Type of element
        measurement_name: Name of secondary measurement (e.g., 'plaster')
    
    Returns:
        True if enabled successfully, False otherwise
    """
    if element_type not in SECONDARY_MEASUREMENTS:
        return False
    
    for strategy in SECONDARY_MEASUREMENTS[element_type]:
        if strategy["name"] == measurement_name:
            strategy["enabled"] = True
            return True
    
    return False

def get_supported_element_types() -> List[str]:
    """Get list of all supported element types
    
    Returns:
        List of element type names
    """
    return list(MEASUREMENT_REGISTRY.keys())
