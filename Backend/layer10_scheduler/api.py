from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from productivity_library import load_productivity_library, add_productivity_norm
from task_generator import create_tasks_from_layer8
from dependency_engine import assign_dependencies, add_custom_dependency, load_dependency_rules
from cpm_engine import calculate_schedule, calculate_late_times
from critical_path import analyze_schedule, get_critical_path

app = FastAPI(title="Layer 11 - Explainable Scheduling Engine API")

class Layer8Item(BaseModel):
    description: str
    quantity: float
    unit: str

class ScheduleRequest(BaseModel):
    layer8_output: List[Layer8Item]
    crews_config: Optional[Dict[str, int]] = None
    custom_dependencies: Optional[Dict[str, List[str]]] = None

class ProductivityNorm(BaseModel):
    task_name: str
    productivity: float
    unit: str

@app.get("/")
def root():
    return {
        "message": "Layer 11 - Explainable Scheduling Engine API",
        "endpoints": {
            "/generate_schedule": "Generate complete project schedule",
            "/productivity_library": "Get all productivity norms",
            "/add_productivity": "Add/update productivity norm",
            "/critical_path": "Get critical path analysis",
            "/gantt_data": "Get Gantt chart data"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy", "layer": 11}

@app.post("/generate_schedule")
def generate_schedule(request: ScheduleRequest):
    """
    Generate complete project schedule from Layer 8 output
    
    Returns schedule with tasks, durations, dependencies, and critical path
    """
    try:
        # Load productivity library
        library = load_productivity_library()
        
        # Convert Layer 8 output to dict format
        layer8_data = [item.dict() for item in request.layer8_output]
        
        # Generate tasks
        tasks = create_tasks_from_layer8(layer8_data, library, request.crews_config)
        
        if not tasks:
            raise HTTPException(status_code=400, detail="No tasks generated. Check if productivity norms exist for materials.")
        
        # Load and apply dependencies
        dependency_rules = load_dependency_rules()
        if request.custom_dependencies:
            dependency_rules.update(request.custom_dependencies)
        
        tasks = assign_dependencies(tasks, dependency_rules)
        
        # Calculate schedule
        tasks = calculate_schedule(tasks)
        tasks = calculate_late_times(tasks)
        
        # Analyze schedule
        analysis = analyze_schedule(tasks)
        
        # Add detailed task list
        analysis["tasks"] = [
            {
                "task_name": t["task_name"],
                "quantity": t["quantity"],
                "unit": t["unit"],
                "productivity": t["productivity"],
                "crews": t["crews"],
                "duration_days": t["duration_days"],
                "dependencies": t["dependencies"],
                "early_start": t["ES"],
                "early_finish": t["EF"],
                "late_start": t.get("LS", 0),
                "late_finish": t.get("LF", 0),
                "float": t.get("float", 0),
                "is_critical": t.get("float", 0) <= 0.01
            }
            for t in tasks
        ]
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/productivity_library")
def get_productivity_library():
    """Get all productivity norms"""
    try:
        library = load_productivity_library()
        return {"productivity_norms": library, "count": len(library)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_productivity")
def add_productivity(norm: ProductivityNorm):
    """Add or update a productivity norm"""
    try:
        library = add_productivity_norm(norm.task_name, norm.productivity, norm.unit)
        return {
            "message": f"Productivity norm for '{norm.task_name}' added/updated",
            "norm": library[norm.task_name]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gantt_data")
def get_gantt_data(request: ScheduleRequest):
    """Get Gantt chart ready data"""
    try:
        library = load_productivity_library()
        layer8_data = [item.dict() for item in request.layer8_output]
        
        tasks = create_tasks_from_layer8(layer8_data, library, request.crews_config)
        
        dependency_rules = load_dependency_rules()
        if request.custom_dependencies:
            dependency_rules.update(request.custom_dependencies)
        
        tasks = assign_dependencies(tasks, dependency_rules)
        tasks = calculate_schedule(tasks)
        
        gantt_data = [
            {
                "task": t["task_name"],
                "start": t["ES"],
                "finish": t["EF"],
                "duration": t["duration_days"],
                "dependencies": t["dependencies"]
            }
            for t in tasks
        ]
        
        return {
            "gantt_data": gantt_data,
            "project_duration": max(t["EF"] for t in tasks) if tasks else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
