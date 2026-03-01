def get_project_duration(tasks):
    """
    Get total project duration (maximum EF)
    
    Args:
        tasks: List of task dictionaries with EF calculated
    
    Returns:
        Project duration in days
    """
    if not tasks:
        return 0
    return max(task["EF"] for task in tasks)

def get_critical_tasks(tasks):
    """
    Identify tasks on the critical path (zero float)
    
    Args:
        tasks: List of task dictionaries with float calculated
    
    Returns:
        List of critical tasks
    """
    critical = []
    for task in tasks:
        # Critical tasks have zero or near-zero float
        if "float" in task and task["float"] <= 0.01:
            critical.append(task)
    return critical

def get_critical_path(tasks):
    """
    Get the sequence of tasks forming the critical path
    
    Args:
        tasks: List of task dictionaries
    
    Returns:
        List of task names in critical path order
    """
    critical_tasks = get_critical_tasks(tasks)
    
    # Sort by ES to get chronological order
    critical_tasks.sort(key=lambda t: t["ES"])
    
    return [task["task_name"] for task in critical_tasks]

def analyze_schedule(tasks):
    """
    Comprehensive schedule analysis with explainability
    
    Args:
        tasks: List of task dictionaries
    
    Returns:
        Dictionary with schedule metrics and explanations
    """
    project_duration = get_project_duration(tasks)
    critical_tasks = get_critical_tasks(tasks)
    critical_path = get_critical_path(tasks)
    
    # Calculate statistics
    total_work_days = sum(task["duration_days"] for task in tasks)
    avg_duration = total_work_days / len(tasks) if tasks else 0
    
    # Find tasks with most float (flexibility)
    flexible_tasks = sorted(
        [t for t in tasks if "float" in t and t["float"] > 0],
        key=lambda t: t["float"],
        reverse=True
    )[:5]
    
    # Build explanations
    explanations = []
    for task in tasks:
        calc = task.get("calculation", "")
        if calc:
            explanations.append(
                f"{task['task_name']}: Duration = {calc} = {task['duration_days']} days"
            )
    
    return {
        "project_duration_days": round(project_duration, 2),
        "total_tasks": len(tasks),
        "critical_tasks_count": len(critical_tasks),
        "critical_path": critical_path,
        "total_work_days": round(total_work_days, 2),
        "average_task_duration": round(avg_duration, 2),
        "critical_tasks": [
            {
                "task_name": t["task_name"],
                "duration": t["duration_days"],
                "start": t["ES"],
                "finish": t["EF"],
                "calculation": t.get("calculation", "")
            }
            for t in critical_tasks
        ],
        "flexible_tasks": [
            {
                "task_name": t["task_name"],
                "float_days": round(t["float"], 2),
                "explanation": f"Can be delayed by {round(t['float'], 2)} days without affecting project completion"
            }
            for t in flexible_tasks
        ],
        "duration_calculations": explanations
    }
