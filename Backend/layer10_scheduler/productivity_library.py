import json
import os

def load_productivity_library(path=None):
    """
    Load productivity norms from JSON file
    
    Args:
        path: Path to productivity library JSON (optional)
    
    Returns:
        Dictionary of productivity norms
    """
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "data", "productivity_library.json")
    
    with open(path, "r") as f:
        return json.load(f)

def get_productivity(task_name, library):
    """
    Get productivity norm for a specific task
    
    Args:
        task_name: Name of the task
        library: Productivity library dictionary
    
    Returns:
        Productivity data or None if not found
    """
    return library.get(task_name)

def add_productivity_norm(task_name, productivity, unit, library_path=None):
    """
    Add or update a productivity norm
    
    Args:
        task_name: Name of the task
        productivity: Productivity value
        unit: Unit of measurement
        library_path: Path to library file (optional)
    """
    if library_path is None:
        library_path = os.path.join(os.path.dirname(__file__), "data", "productivity_library.json")
    
    library = load_productivity_library(library_path)
    library[task_name] = {
        "productivity": productivity,
        "unit": unit
    }
    
    with open(library_path, "w") as f:
        json.dump(library, f, indent=2)
    
    return library
