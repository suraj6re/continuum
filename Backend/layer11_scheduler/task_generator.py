def calculate_duration(quantity, productivity, crews=1):
    """
    Calculate task duration based on quantity and productivity
    
    Formula: Duration = Quantity / (Productivity × Crews)
    
    Args:
        quantity: Total quantity of work
        productivity: Productivity rate (units/day)
        crews: Number of crews working (default: 1)
    
    Returns:
        Duration in days (rounded to 2 decimals)
    """
    if productivity * crews == 0:
        raise ValueError("Productivity or crews cannot be zero")
    
    duration = quantity / (productivity * crews)
    return round(duration, 2)

def create_task(task_name, quantity, productivity, unit, crews=1):
    """
    Create a task with calculated duration
    
    Args:
        task_name: Name of the task
        quantity: Total quantity
        productivity: Productivity rate
        unit: Unit of measurement
        crews: Number of crews (default: 1)
    
    Returns:
        Task dictionary with duration and calculation explanation
    """
    duration = calculate_duration(quantity, productivity, crews)
    
    return {
        "task_name": task_name,
        "quantity": quantity,
        "productivity": productivity,
        "unit": unit,
        "crews": crews,
        "duration_days": duration,
        "calculation": f"{quantity} / ({productivity} × {crews})",
        "dependencies": [],
        "ES": 0,
        "EF": 0,
        "LS": 0,
        "LF": 0,
        "float": 0
    }

def create_tasks_from_layer8(layer8_output, productivity_library, crews_config=None):
    """
    Generate tasks from Layer 8 output
    
    Args:
        layer8_output: List of items from Layer 8 with description, quantity, unit
        productivity_library: Productivity norms dictionary
        crews_config: Dictionary mapping task names to crew counts (optional)
    
    Returns:
        List of task dictionaries
    """
    if crews_config is None:
        crews_config = {}
    
    tasks = []
    
    for item in layer8_output:
        task_name = item.get("description")
        quantity = item.get("quantity")
        unit = item.get("unit")
        
        # Get productivity from library
        prod_data = productivity_library.get(task_name)
        if not prod_data:
            # Skip if no productivity data available
            continue
        
        productivity = prod_data["productivity"]
        crews = crews_config.get(task_name, 1)
        
        task = create_task(task_name, quantity, productivity, unit, crews)
        tasks.append(task)
    
    return tasks
