from productivity_library import load_productivity_library, get_productivity
from task_generator import create_task, create_tasks_from_layer8
from dependency_engine import assign_dependencies, validate_dependencies
from cpm_engine import calculate_schedule, calculate_late_times
from critical_path import get_project_duration, get_critical_path, analyze_schedule
import json

def test_productivity_library():
    """Test 1: Load and access productivity library"""
    print("=" * 80)
    print("TEST 1: Productivity Library")
    print("=" * 80)
    
    library = load_productivity_library()
    print(f"Loaded {len(library)} productivity norms")
    
    steel = get_productivity("Steel Reinforcement", library)
    print(f"\nSteel Reinforcement: {steel['productivity']} {steel['unit']}")
    
    concrete = get_productivity("Concrete Slab", library)
    print(f"Concrete Slab: {concrete['productivity']} {concrete['unit']}")
    
    print("\n[OK] Test 1 Complete\n")

def test_task_generation():
    """Test 2: Generate tasks with durations"""
    print("=" * 80)
    print("TEST 2: Task Generation")
    print("=" * 80)
    
    task1 = create_task("Steel Reinforcement", 5000, 1000, "kg", crews=2)
    print(f"Task: {task1['task_name']}")
    print(f"Quantity: {task1['quantity']} {task1['unit']}")
    print(f"Productivity: {task1['productivity']} {task1['unit']}/day")
    print(f"Crews: {task1['crews']}")
    print(f"Duration: {task1['duration_days']} days")
    
    task2 = create_task("Concrete Slab", 200, 50, "m2", crews=2)
    print(f"\nTask: {task2['task_name']}")
    print(f"Quantity: {task2['quantity']} {task2['unit']}")
    print(f"Duration: {task2['duration_days']} days")
    
    print("\n[OK] Test 2 Complete\n")

def test_dependencies():
    """Test 3: Assign dependencies"""
    print("=" * 80)
    print("TEST 3: Dependency Assignment")
    print("=" * 80)
    
    tasks = [
        create_task("Steel Reinforcement", 5000, 1000, "kg", crews=2),
        create_task("Concrete Slab", 200, 50, "m2", crews=2),
        create_task("Brickwork", 100, 25, "m3", crews=1)
    ]
    
    tasks = assign_dependencies(tasks)
    
    for task in tasks:
        deps = ", ".join(task["dependencies"]) if task["dependencies"] else "None"
        print(f"{task['task_name']}: depends on [{deps}]")
    
    is_valid, missing = validate_dependencies(tasks)
    print(f"\nDependencies valid: {is_valid}")
    
    print("\n[OK] Test 3 Complete\n")

def test_schedule_calculation():
    """Test 4: Calculate schedule with CPM"""
    print("=" * 80)
    print("TEST 4: Schedule Calculation (CPM)")
    print("=" * 80)
    
    tasks = [
        create_task("Steel Reinforcement", 5000, 1000, "kg", crews=2),
        create_task("Concrete Slab", 200, 50, "m2", crews=2),
        create_task("Brickwork", 100, 25, "m3", crews=1)
    ]
    
    tasks = assign_dependencies(tasks)
    tasks = calculate_schedule(tasks)
    
    print(f"{'Task':<25} {'Duration':<10} {'ES':<8} {'EF':<8}")
    print("-" * 60)
    for task in tasks:
        print(f"{task['task_name']:<25} {task['duration_days']:<10} {task['ES']:<8} {task['EF']:<8}")
    
    duration = get_project_duration(tasks)
    print(f"\nTotal Project Duration: {duration} days")
    
    print("\n[OK] Test 4 Complete\n")

def test_critical_path():
    """Test 5: Identify critical path"""
    print("=" * 80)
    print("TEST 5: Critical Path Analysis")
    print("=" * 80)
    
    tasks = [
        create_task("Steel Reinforcement", 5000, 1000, "kg", crews=2),
        create_task("Concrete Slab", 200, 50, "m2", crews=2),
        create_task("Brickwork", 100, 25, "m3", crews=1)
    ]
    
    tasks = assign_dependencies(tasks)
    tasks = calculate_schedule(tasks)
    tasks = calculate_late_times(tasks)
    
    critical_path = get_critical_path(tasks)
    print(f"Critical Path: {' -> '.join(critical_path)}")
    
    print(f"\n{'Task':<25} {'Float':<10} {'Critical':<10}")
    print("-" * 50)
    for task in tasks:
        is_critical = "YES" if task.get("float", 0) <= 0.01 else "NO"
        print(f"{task['task_name']:<25} {task.get('float', 0):<10.2f} {is_critical:<10}")
    
    print("\n[OK] Test 5 Complete\n")

def test_layer8_integration():
    """Test 6: Integration with Layer 8 output"""
    print("=" * 80)
    print("TEST 6: Layer 8 Integration")
    print("=" * 80)
    
    # Simulated Layer 8 output
    layer8_output = [
        {"description": "Steel Reinforcement", "quantity": 5000, "unit": "kg"},
        {"description": "Concrete Slab", "quantity": 200, "unit": "m2"},
        {"description": "Brickwork", "quantity": 100, "unit": "m3"}
    ]
    
    print("Layer 8 Input:")
    print(json.dumps(layer8_output, indent=2))
    
    library = load_productivity_library()
    crews_config = {
        "Steel Reinforcement": 2,
        "Concrete Slab": 2,
        "Brickwork": 1
    }
    
    tasks = create_tasks_from_layer8(layer8_output, library, crews_config)
    tasks = assign_dependencies(tasks)
    tasks = calculate_schedule(tasks)
    
    print(f"\nGenerated {len(tasks)} tasks")
    print(f"Project Duration: {get_project_duration(tasks)} days")
    
    print("\n[OK] Test 6 Complete\n")

def test_complete_analysis():
    """Test 7: Complete schedule analysis"""
    print("=" * 80)
    print("TEST 7: Complete Schedule Analysis")
    print("=" * 80)
    
    # Simulated Layer 8 output
    layer8_output = [
        {"description": "Excavation", "quantity": 150, "unit": "m3"},
        {"description": "Foundation", "quantity": 50, "unit": "m3"},
        {"description": "Steel Reinforcement", "quantity": 5000, "unit": "kg"},
        {"description": "Column Casting", "quantity": 30, "unit": "m3"},
        {"description": "Beam Casting", "quantity": 40, "unit": "m3"},
        {"description": "Concrete Slab", "quantity": 200, "unit": "m2"},
        {"description": "Brickwork", "quantity": 100, "unit": "m3"},
        {"description": "Plastering", "quantity": 300, "unit": "m2"}
    ]
    
    library = load_productivity_library()
    crews_config = {
        "Excavation": 2,
        "Foundation": 2,
        "Steel Reinforcement": 2,
        "Column Casting": 1,
        "Beam Casting": 1,
        "Concrete Slab": 2,
        "Brickwork": 2,
        "Plastering": 2
    }
    
    tasks = create_tasks_from_layer8(layer8_output, library, crews_config)
    tasks = assign_dependencies(tasks)
    tasks = calculate_schedule(tasks)
    tasks = calculate_late_times(tasks)
    
    analysis = analyze_schedule(tasks)
    
    print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    print("\n[OK] Test 7 Complete\n")

def test_gantt_output():
    """Test 8: Gantt chart ready output"""
    print("=" * 80)
    print("TEST 8: Gantt Chart Output")
    print("=" * 80)
    
    layer8_output = [
        {"description": "Steel Reinforcement", "quantity": 5000, "unit": "kg"},
        {"description": "Concrete Slab", "quantity": 200, "unit": "m2"},
        {"description": "Brickwork", "quantity": 100, "unit": "m3"}
    ]
    
    library = load_productivity_library()
    tasks = create_tasks_from_layer8(layer8_output, library, {"Steel Reinforcement": 2, "Concrete Slab": 2, "Brickwork": 1})
    tasks = assign_dependencies(tasks)
    tasks = calculate_schedule(tasks)
    
    gantt_data = []
    for task in tasks:
        gantt_data.append({
            "task": task["task_name"],
            "start": task["ES"],
            "finish": task["EF"],
            "duration": task["duration_days"]
        })
    
    print("Gantt Chart Data:")
    print(json.dumps(gantt_data, indent=2, ensure_ascii=False))
    
    print("\n[OK] Test 8 Complete\n")

def main():
    print("\n" + "=" * 80)
    print("LAYER 11 - EXPLAINABLE SCHEDULING ENGINE")
    print("=" * 80 + "\n")
    
    test_productivity_library()
    test_task_generation()
    test_dependencies()
    test_schedule_calculation()
    test_critical_path()
    test_layer8_integration()
    test_complete_analysis()
    test_gantt_output()
    
    print("=" * 80)
    print("ALL TESTS COMPLETE - LAYER 11 READY")
    print("=" * 80)

if __name__ == "__main__":
    main()
