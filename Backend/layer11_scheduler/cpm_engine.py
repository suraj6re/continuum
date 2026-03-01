import networkx as nx

def run_cpm(tasks):
    """
    Run Critical Path Method using NetworkX
    
    Args:
        tasks: List of task dictionaries with dependencies
    
    Returns:
        NetworkX DiGraph with ES/EF calculated
    """
    G = nx.DiGraph()
    
    # Add nodes with duration
    for task in tasks:
        G.add_node(
            task["task_name"],
            duration=task["duration_days"],
            quantity=task["quantity"],
            unit=task["unit"],
            productivity=task["productivity"],
            crews=task["crews"],
            calculation=task.get("calculation", "")
        )
    
    # Add edges (dependencies)
    for task in tasks:
        for dep in task["dependencies"]:
            G.add_edge(dep, task["task_name"])
    
    # Forward pass - Calculate ES and EF
    for node in nx.topological_sort(G):
        preds = list(G.predecessors(node))
        
        if not preds:
            G.nodes[node]["ES"] = 0
        else:
            G.nodes[node]["ES"] = max(
                G.nodes[p]["EF"] for p in preds
            )
        
        duration = G.nodes[node].get("duration", 0)
        G.nodes[node]["EF"] = G.nodes[node]["ES"] + duration
    
    # Backward pass - Calculate LS and LF
    total_duration = max(G.nodes[n]["EF"] for n in G.nodes)
    
    for node in reversed(list(nx.topological_sort(G))):
        succs = list(G.successors(node))
        
        if not succs:
            G.nodes[node]["LF"] = total_duration
        else:
            G.nodes[node]["LF"] = min(
                G.nodes[s]["LS"] for s in succs
            )
        
        duration = G.nodes[node].get("duration", 0)
        G.nodes[node]["LS"] = G.nodes[node]["LF"] - duration
        
        # Calculate float
        G.nodes[node]["float"] = G.nodes[node]["LS"] - G.nodes[node]["ES"]
    
    return G

def topological_sort(tasks):
    """
    Sort tasks in topological order (dependencies first)
    Kept for backward compatibility
    """
    task_map = {t["task_name"]: t for t in tasks}
    visited = set()
    result = []
    
    def visit(task_name):
        if task_name in visited:
            return
        visited.add(task_name)
        
        task = task_map.get(task_name)
        if task:
            for dep in task["dependencies"]:
                if dep in task_map:
                    visit(dep)
            result.append(task)
    
    for task in tasks:
        visit(task["task_name"])
    
    return result

def calculate_schedule(tasks):
    """
    Calculate schedule using NetworkX CPM
    Wrapper for backward compatibility
    """
    G = run_cpm(tasks)
    
    # Update tasks with calculated values
    for task in tasks:
        node_data = G.nodes[task["task_name"]]
        task["ES"] = node_data["ES"]
        task["EF"] = node_data["EF"]
        task["LS"] = node_data.get("LS", 0)
        task["LF"] = node_data.get("LF", 0)
        task["float"] = node_data.get("float", 0)
    
    return tasks

def calculate_late_times(tasks, project_duration=None):
    """
    Calculate late times - now handled by run_cpm
    Kept for backward compatibility
    """
    return tasks
