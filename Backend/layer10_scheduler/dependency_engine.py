import json
import os

# Default dependency rules for construction activities
DEFAULT_DEPENDENCY_RULES = {
    "Excavation": [],
    "Foundation": ["Excavation"],
    "Steel Reinforcement": ["Foundation"],
    "Column Casting": ["Steel Reinforcement"],
    "Beam Casting": ["Column Casting"],
    "Concrete Slab": ["Beam Casting"],
    "Reinforced Cement Concrete M25": ["Steel Reinforcement"],
    "Brickwork": ["Concrete Slab"],
    "Plastering": ["Brickwork"],
    "Flooring": ["Plastering"]
}

def load_dependency_rules(path=None):
    """
    Load dependency rules from JSON file or use defaults
    
    Args:
        path: Path to dependency rules JSON (optional)
    
    Returns:
        Dictionary of dependency rules
    """
    if path and os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return DEFAULT_DEPENDENCY_RULES.copy()

def assign_dependencies(task_list, dependency_rules=None):
    """
    Assign dependencies to tasks based on rules
    
    Args:
        task_list: List of task dictionaries
        dependency_rules: Dictionary of dependency rules (optional)
    
    Returns:
        Task list with dependencies assigned
    """
    if dependency_rules is None:
        dependency_rules = DEFAULT_DEPENDENCY_RULES
    
    for task in task_list:
        task_name = task["task_name"]
        task["dependencies"] = dependency_rules.get(task_name, [])
    
    return task_list

def add_custom_dependency(task_name, depends_on, rules=None):
    """
    Add a custom dependency rule
    
    Args:
        task_name: Name of the task
        depends_on: List of tasks this task depends on
        rules: Existing rules dictionary (optional)
    
    Returns:
        Updated rules dictionary
    """
    if rules is None:
        rules = DEFAULT_DEPENDENCY_RULES.copy()
    
    rules[task_name] = depends_on
    return rules

def validate_dependencies(task_list):
    """
    Validate that all dependencies exist in task list
    
    Args:
        task_list: List of task dictionaries
    
    Returns:
        Tuple (is_valid, missing_dependencies)
    """
    task_names = {task["task_name"] for task in task_list}
    missing = []
    
    for task in task_list:
        for dep in task["dependencies"]:
            if dep not in task_names:
                missing.append((task["task_name"], dep))
    
    return len(missing) == 0, missing
