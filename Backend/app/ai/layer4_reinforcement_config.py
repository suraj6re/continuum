"""Layer 4 Step B1: Reinforcement Configuration (Configurable Ratios)"""
from typing import Dict, Optional

# Default reinforcement ratios (kg per cubic meter of concrete)
# These are industry-standard estimates and can be overridden per project
DEFAULT_REINFORCEMENT_RATIOS = {
    "Slab": {
        "steel_ratio": 80,  # kg/m³
        "unit": "kg/m³",
        "description": "Standard slab reinforcement"
    },
    "Column": {
        "steel_ratio": 120,  # kg/m³
        "unit": "kg/m³",
        "description": "Standard column reinforcement"
    },
    "Beam": {
        "steel_ratio": 100,  # kg/m³
        "unit": "kg/m³",
        "description": "Standard beam reinforcement"
    },
    "Wall": {
        "steel_ratio": 60,  # kg/m³
        "unit": "kg/m³",
        "description": "RCC wall reinforcement"
    },
    "Footing": {
        "steel_ratio": 90,  # kg/m³
        "unit": "kg/m³",
        "description": "Foundation footing reinforcement"
    }
}

def get_reinforcement_ratio(element_type: str, 
                            project_config: Optional[Dict] = None) -> Optional[Dict]:
    """Get reinforcement ratio for element type with project override support
    
    Priority:
    1. Project-specific config (if provided)
    2. Default ratios
    
    Args:
        element_type: Type of element (Slab, Column, etc.)
        project_config: Optional project-specific ratio overrides
    
    Returns:
        Ratio configuration dict or None if not found
    """
    # Check project config first (highest priority)
    if project_config and element_type in project_config:
        return project_config[element_type]
    
    # Fall back to defaults
    return DEFAULT_REINFORCEMENT_RATIOS.get(element_type)

def load_project_config(config_source: Dict) -> Dict:
    """Load project-specific reinforcement ratios
    
    This allows per-project customization based on:
    - Seismic zone
    - Building type
    - Local codes
    - Engineer preferences
    
    Args:
        config_source: Dict with project-specific ratios
    
    Returns:
        Validated project config
    """
    validated_config = {}
    
    for element_type, config in config_source.items():
        if isinstance(config, dict) and "steel_ratio" in config:
            validated_config[element_type] = {
                "steel_ratio": float(config["steel_ratio"]),
                "unit": config.get("unit", "kg/m³"),
                "description": config.get("description", f"Project override for {element_type}")
            }
        elif isinstance(config, (int, float)):
            # Allow simple number format
            validated_config[element_type] = {
                "steel_ratio": float(config),
                "unit": "kg/m³",
                "description": f"Project override for {element_type}"
            }
    
    return validated_config

def get_all_supported_types() -> list:
    """Get list of all element types with reinforcement ratios
    
    Returns:
        List of element type names
    """
    return list(DEFAULT_REINFORCEMENT_RATIOS.keys())

def get_ratio_value(element_type: str, project_config: Optional[Dict] = None) -> Optional[float]:
    """Get just the ratio value (convenience function)
    
    Args:
        element_type: Type of element
        project_config: Optional project config
    
    Returns:
        Steel ratio value or None
    """
    config = get_reinforcement_ratio(element_type, project_config)
    return config["steel_ratio"] if config else None
