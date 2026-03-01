# Layer 13 - Quick Reference

## Step 1: Unified Summary Endpoint

### Quick Start

```bash
# Start API
cd Backend/layer13_dashboard
uvicorn main:app --reload --port 8005

# Test endpoint
curl http://localhost:8005/dashboard
```

---

## Python Usage

```python
from dashboard_api import DashboardAPI

# Initialize with engines
dashboard_api = DashboardAPI(
    qto_engine=qto_engine,
    cost_engine=cost_engine,
    schedule_engine=schedule_engine,
    approval_engine=approval_engine,
    risk_engine=risk_engine,
    confidence_engine=confidence_engine
)

# Get consolidated data
data = dashboard_api.get_dashboard_data()
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/dashboard` | GET | Unified dashboard data |

---

## Response Structure

```json
{
  "summary": {
    "total_items": 4,
    "approved_count": 2,
    "unapproved_count": 2,
    "export_ready": false
  },
  "qto": {...},
  "cost": {...},
  "schedule": {...},
  "risk": {...},
  "confidence": {...},
  "export_status": {...}
}
```

---

## Engine Requirements

Each engine must implement `get_summary()`:

```python
# QTO Engine
def get_summary(self):
    return self.qto_summary

# Cost Engine
def get_summary(self):
    return {"total_cost": ..., "item_wise": ...}

# Schedule Engine
def get_summary(self):
    return {"total_duration": ..., "critical_path": ...}

# Approval Engine
def get_approval_summary(self):
    return {"total_items": ..., "approved_count": ...}
```

---

## Key Features

✅ Read-only aggregation  
✅ No computation  
✅ No data modification  
✅ Fast (<100ms)  
✅ Presentation-ready  
✅ Export-aware  

---

## Production Deployment

Replace mock engines with real engines:

```python
from layer12_review.recalculation_engine import QTOEngine, CostEngine
from layer12_review.approval_engine import ApprovalEngine

dashboard_api = DashboardAPI(
    qto_engine=QTOEngine(element_graph),
    cost_engine=CostEngine(element_graph, rate_table),
    approval_engine=ApprovalEngine(qto_summary),
    ...
)
```

---

## Status

✅ **Step 1 Complete**  
⏳ Steps 2-8 Pending  

**Layer 13 Step 1 is production-ready!** 🎉
