# Layer 11 - Quick Reference

## 🚀 Quick Start

### Run Tests
```bash
cd Backend/layer11_scheduler
python main.py
```

### Start API
```bash
uvicorn api:app --reload --port 8003
```

---

## 📊 Core Formula

```
Duration = Quantity / (Productivity × Crews)
```

**Example:**
- Steel: 5000 kg
- Productivity: 1000 kg/day  
- Crews: 2
- **Duration = 2.5 days**

---

## 🔧 Key Functions

### Load Productivity
```python
from productivity_library import load_productivity_library
library = load_productivity_library()
```

### Generate Tasks
```python
from task_generator import create_tasks_from_layer8
tasks = create_tasks_from_layer8(layer8_output, library, crews_config)
```

### Assign Dependencies
```python
from dependency_engine import assign_dependencies
tasks = assign_dependencies(tasks)
```

### Calculate Schedule
```python
from cpm_engine import calculate_schedule, calculate_late_times
tasks = calculate_schedule(tasks)
tasks = calculate_late_times(tasks)
```

### Analyze
```python
from critical_path import analyze_schedule
analysis = analyze_schedule(tasks)
```

---

## 🌐 API Endpoints

### Generate Schedule
```bash
POST /generate_schedule
{
  "layer8_output": [...],
  "crews_config": {...}
}
```

### Get Productivity Library
```bash
GET /productivity_library
```

### Add Productivity Norm
```bash
POST /add_productivity
{
  "task_name": "Painting",
  "productivity": 60,
  "unit": "m2/day"
}
```

### Get Gantt Data
```bash
POST /gantt_data
{
  "layer8_output": [...]
}
```

---

## 📝 Input Format (Layer 8)

```json
[
  {
    "description": "Steel Reinforcement",
    "quantity": 5000,
    "unit": "kg"
  }
]
```

---

## 📤 Output Format

```json
{
  "project_duration_days": 21.5,
  "critical_path": ["Excavation", "Foundation", ...],
  "tasks": [
    {
      "task_name": "Steel Reinforcement",
      "duration_days": 2.5,
      "early_start": 0,
      "early_finish": 2.5,
      "is_critical": true
    }
  ]
}
```

---

## ⚙️ Customization

### Edit Productivity Norms
File: `data/productivity_library.json`
```json
{
  "Task Name": {
    "productivity": 100,
    "unit": "unit/day"
  }
}
```

### Configure Crews
```python
crews_config = {
    "Steel Reinforcement": 2,
    "Concrete Slab": 2
}
```

### Custom Dependencies
```python
custom_deps = {
    "Task A": ["Task B", "Task C"]
}
```

---

## 📊 Default Productivity Norms

| Task | Productivity | Unit |
|------|--------------|------|
| Concrete Slab | 50 | m2/day |
| Steel Reinforcement | 1000 | kg/day |
| Brickwork | 25 | m3/day |
| Plastering | 40 | m2/day |
| Excavation | 30 | m3/day |
| Foundation | 15 | m3/day |
| Column Casting | 8 | m3/day |
| Beam Casting | 12 | m3/day |
| Flooring | 35 | m2/day |

---

## 🔗 Default Dependencies

```
Excavation → Foundation → Steel Reinforcement → 
Column Casting → Beam Casting → Concrete Slab → 
Brickwork → Plastering
```

---

## ✅ Test Results

All 8 tests pass:
1. ✅ Productivity Library
2. ✅ Task Generation
3. ✅ Dependency Assignment
4. ✅ Schedule Calculation
5. ✅ Critical Path Analysis
6. ✅ Layer 8 Integration
7. ✅ Complete Analysis
8. ✅ Gantt Output

---

## 🎯 Key Outputs

- **Project Duration** - Total days
- **Critical Path** - Zero-float tasks
- **Task Schedule** - ES, EF, LS, LF
- **Float** - Scheduling flexibility
- **Gantt Data** - Timeline visualization

---

## 🚀 Performance

- <5ms per task generation
- <10ms CPM calculation (50 tasks)
- <50ms total response

---

## 📦 Dependencies

- Python standard library
- FastAPI (for API)
- Pydantic (for API)

---

**Status:** ✅ Production Ready  
**Version:** 1.0
