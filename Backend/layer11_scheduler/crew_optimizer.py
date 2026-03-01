def optimize_crews(task, target_duration, productivity):
    """
    Calculate required crews to achieve target duration
    
    Args:
        task: Task dictionary
        target_duration: Desired duration in days
        productivity: Productivity rate
    
    Returns:
        Dictionary with optimization results and explanation
    """
    quantity = task["quantity"]
    current_crews = task["crews"]
    current_duration = task["duration_days"]
    
    # Calculate required crews
    required_crews = quantity / (productivity * target_duration)
    required_crews = max(1, round(required_crews))
    
    # Calculate actual duration with required crews
    optimized_duration = quantity / (productivity * required_crews)
    
    explanation = (
        f"Duration reduced from {current_duration} days to {round(optimized_duration, 2)} days "
        f"by increasing crews from {current_crews} to {required_crews}."
    )
    
    return {
        "task_name": task["task_name"],
        "baseline_duration": current_duration,
        "baseline_crews": current_crews,
        "optimized_duration": round(optimized_duration, 2),
        "optimized_crews": required_crews,
        "time_saved": round(current_duration - optimized_duration, 2),
        "explanation": explanation,
        "tradeoff": f"Requires {required_crews - current_crews} additional crew(s)"
    }

def compare_crew_scenarios(task, productivity, crew_options):
    """
    Compare multiple crew scenarios
    
    Args:
        task: Task dictionary
        productivity: Productivity rate
        crew_options: List of crew counts to compare
    
    Returns:
        List of scenarios with explanations
    """
    quantity = task["quantity"]
    scenarios = []
    
    for crews in crew_options:
        duration = quantity / (productivity * crews)
        
        scenarios.append({
            "crews": crews,
            "duration_days": round(duration, 2),
            "calculation": f"{quantity} / ({productivity} x {crews})",
            "explanation": f"With {crews} crew(s): {round(duration, 2)} days"
        })
    
    return {
        "task_name": task["task_name"],
        "quantity": quantity,
        "productivity": productivity,
        "unit": task["unit"],
        "scenarios": scenarios,
        "recommendation": min(scenarios, key=lambda x: x["duration_days"])
    }

def explain_schedule_changes(baseline_tasks, optimized_tasks):
    """
    Explain differences between baseline and optimized schedules
    
    Args:
        baseline_tasks: Original task list
        optimized_tasks: Optimized task list
    
    Returns:
        Dictionary with change explanations
    """
    baseline_map = {t["task_name"]: t for t in baseline_tasks}
    changes = []
    
    for opt_task in optimized_tasks:
        task_name = opt_task["task_name"]
        if task_name in baseline_map:
            base_task = baseline_map[task_name]
            
            if base_task["crews"] != opt_task["crews"]:
                changes.append({
                    "task": task_name,
                    "change_type": "crew_increase",
                    "from_crews": base_task["crews"],
                    "to_crews": opt_task["crews"],
                    "from_duration": base_task["duration_days"],
                    "to_duration": opt_task["duration_days"],
                    "time_saved": round(base_task["duration_days"] - opt_task["duration_days"], 2),
                    "explanation": (
                        f"{task_name}: Crews increased from {base_task['crews']} to {opt_task['crews']}, "
                        f"reducing duration from {base_task['duration_days']} to {opt_task['duration_days']} days"
                    )
                })
    
    baseline_duration = max(t["EF"] for t in baseline_tasks) if baseline_tasks else 0
    optimized_duration = max(t["EF"] for t in optimized_tasks) if optimized_tasks else 0
    
    return {
        "baseline_duration": round(baseline_duration, 2),
        "optimized_duration": round(optimized_duration, 2),
        "time_saved": round(baseline_duration - optimized_duration, 2),
        "changes": changes,
        "summary": (
            f"Project duration reduced from {round(baseline_duration, 2)} days "
            f"to {round(optimized_duration, 2)} days by optimizing crew allocation."
        )
    }
