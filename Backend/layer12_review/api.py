from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional
from element_viewer import ElementViewer
from override_engine import OverrideEngine
from change_log import ChangeLogger
from recalculation_engine import RecalculationEngine, QTOEngine, CostEngine, ScheduleEngine
from approval_engine import ApprovalEngine
import json

app = FastAPI(title="Layer 12 - Human-in-the-Loop Review API (Step 1)")

# Element graph will be loaded from database or previous layer outputs
# This is a placeholder that would be replaced with actual data loading
element_graph = {}

def load_element_graph_from_database():
    """
    Load element graph from database or Layer 5/6 output
    In production, this would connect to MongoDB or read from file
    """
    # This would be replaced with actual database query
    # For now, returns empty dict - will be populated by integration
    return {}

def load_element_graph_from_file(filepath: str):
    """
    Load element graph from JSON file (Layer 5/6 output)
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Initialize all engines (will be updated when data is loaded)
viewer = None
override_engine = None
change_logger = None
recalculation_engine = None
approval_engine = None
qto_summary = {}

@app.on_event("startup")
async def startup_event():
    """Load element graph on startup"""
    global element_graph, viewer, override_engine, change_logger, recalculation_engine, approval_engine, qto_summary
    # Try to load from file first, then database
    element_graph = load_element_graph_from_database()
    
    # Initialize change logger with persistent storage
    change_logger = ChangeLogger(
        storage_path="change_logs.json",
        project_id="default_project"
    )
    
    # Initialize QTO summary (in production, this comes from Layer 4-6)
    qto_summary = {
        "Concrete in Slab": {
            "quantity": 12.45,
            "cost": 85600,
            "status": "Pending"
        },
        "Brickwork": {
            "quantity": 8.23,
            "cost": 34200,
            "status": "Approved"
        }
    }
    
    # Initialize recalculation engines
    qto_engine = QTOEngine(element_graph)
    cost_engine = CostEngine(element_graph, rate_table={"RCC": 7000, "Brick": 5000})
    schedule_engine = ScheduleEngine(element_graph, productivity_table={"Wall": 5, "Slab": 10, "Column": 3})
    
    # Initialize approval engine
    approval_engine = ApprovalEngine(qto_summary)
    
    viewer = ElementViewer(element_graph)
    override_engine = OverrideEngine(element_graph, change_logger)
    recalculation_engine = RecalculationEngine(element_graph, qto_engine, cost_engine, schedule_engine, approval_engine)

@app.get("/")
def root():
    return {
        "message": "Layer 12 - Human-in-the-Loop Review API (Steps 1-5)",
        "description": "Element inspection, override, audit trail, recalculation, and approval",
        "endpoints": {
            "Step 1 - Viewer": {
                "/element/{element_id}": "Get complete element details",
                "/elements/type/{element_type}": "Get all elements of a type",
                "/elements/low-confidence": "Get elements requiring review",
                "/element/{element_id}/formula": "Get element formula breakdown",
                "/elements/summary": "Get summary statistics",
                "/elements/search": "Search elements by criteria"
            },
            "Step 2 - Override": {
                "/element/{element_id}/override/dimension": "Override dimension",
                "/element/{element_id}/override/material": "Override material",
                "/element/{element_id}/verify": "Mark as verified",
                "/element/{element_id}/revert": "Revert to AI values",
                "/overrides/bulk": "Bulk dimension overrides",
                "/overrides/audit": "Get audit log",
                "/overrides/summary": "Get override summary",
                "/overrides/needs-recalc": "Get elements needing recalculation"
            },
            "Step 3 - Change Log": {
                "/changelog/all": "Get all change logs",
                "/changelog/element/{element_id}": "Get element change history",
                "/changelog/user/{user}": "Get user activity",
                "/changelog/summary": "Get change summary",
                "/changelog/export": "Export compliance report"
            },
            "Step 4 - Recalculation": {
                "/recalculate": "Trigger recalculation",
                "/recalculate/preview": "Preview recalculation",
                "/recalculate/status": "Get recalculation status"
            },
            "Step 5 - Approval": {
                "/qto/{item_name}/approve": "Approve QTO item",
                "/qto/{item_name}/reject": "Reject QTO item",
                "/qto/{item_name}/status": "Set QTO item status",
                "/qto/bulk-approve": "Bulk approve items",
                "/qto/unapproved": "Get unapproved items",
                "/qto/status/{status}": "Get items by status",
                "/qto/approval-summary": "Get approval summary",
                "/qto/can-export": "Check if ready for export"
            }
        },
        "principles": [
            "Step 1: Read-only inspection",
            "Step 2: Controlled mutation with audit trail",
            "Step 3: Enterprise-grade change logging",
            "Step 4: User-triggered recalculation",
            "Step 5: Approval governance - only approved items exportable"
        ]
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "layer": 12,
        "step": 1,
        "elements_loaded": len(element_graph)
    }

@app.get("/element/{element_id}")
def get_element(element_id: str):
    """
    Get complete structured details of an element
    
    Returns:
    - Element ID, type, dimensions
    - Material, quantity, formula
    - Confidence score
    - Source traceability
    - Manual override status
    """
    if viewer is None:
        raise HTTPException(status_code=503, detail="Element graph not loaded")
    
    result = viewer.get_element_details(element_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.get("/elements/type/{element_type}")
def get_elements_by_type(element_type: str):
    """
    Get all elements of a specific type (Wall, Slab, Column, etc.)
    """
    if viewer is None:
        raise HTTPException(status_code=503, detail="Element graph not loaded")
    
    results = viewer.get_elements_by_type(element_type)
    
    return {
        "element_type": element_type,
        "count": len(results),
        "elements": results
    }

@app.get("/elements/low-confidence")
def get_low_confidence_elements(threshold: float = Query(0.7, ge=0.0, le=1.0)):
    """
    Get elements below confidence threshold for priority review
    
    Args:
        threshold: Confidence threshold (0.0 to 1.0, default: 0.7)
    """
    if viewer is None:
        raise HTTPException(status_code=503, detail="Element graph not loaded")
    
    results = viewer.get_low_confidence_elements(threshold)
    
    return {
        "threshold": threshold,
        "count": len(results),
        "requires_review": results
    }

@app.get("/element/{element_id}/formula")
def get_element_formula(element_id: str):
    """
    Get detailed formula breakdown for an element
    Shows calculation steps and dimensions used
    """
    if viewer is None:
        raise HTTPException(status_code=503, detail="Element graph not loaded")
    
    result = viewer.get_element_formula(element_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.get("/elements/summary")
def get_elements_summary():
    """
    Get summary statistics of all elements
    - Total count
    - Count by type
    - Low confidence count
    - Manual overrides count
    """
    if viewer is None:
        raise HTTPException(status_code=503, detail="Element graph not loaded")
    
    return viewer.get_all_elements_summary()

class SearchQuery(BaseModel):
    type: Optional[str] = None
    material: Optional[str] = None
    confidence_min: Optional[float] = None
    manual_override: Optional[bool] = None

@app.post("/elements/search")
def search_elements(query: SearchQuery):
    """
    Search elements by multiple criteria
    """
    if viewer is None:
        raise HTTPException(status_code=503, detail="Element graph not loaded")
    
    query_dict = {k: v for k, v in query.dict().items() if v is not None}
    results = viewer.search_elements(query_dict)
    
    return {
        "query": query_dict,
        "count": len(results),
        "results": results
    }

@app.post("/load-element-graph")
def load_element_graph(filepath: str):
    """
    Manually load element graph from file
    (For testing/development)
    """
    global element_graph, viewer
    
    element_graph = load_element_graph_from_file(filepath)
    viewer = ElementViewer(element_graph)
    
    return {
        "message": "Element graph loaded",
        "elements_count": len(element_graph)
    }


# ============================================================================
# STEP 2: OVERRIDE ENGINE ENDPOINTS
# ============================================================================

class DimensionOverride(BaseModel):
    field: str
    new_value: float
    user: Optional[str] = "system"

class MaterialOverride(BaseModel):
    new_material: str
    user: Optional[str] = "system"

class BulkOverride(BaseModel):
    overrides: List[Dict]
    user: Optional[str] = "system"

@app.post("/element/{element_id}/override/dimension")
def override_dimension(element_id: str, override: DimensionOverride):
    """
    Override a dimension field (length, thickness, height, etc.)
    Marks element as manually modified and human-verified
    """
    if override_engine is None:
        raise HTTPException(status_code=503, detail="Override engine not loaded")
    
    result = override_engine.override_dimension(
        element_id,
        override.field,
        override.new_value,
        override.user
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.post("/element/{element_id}/override/material")
def override_material(element_id: str, override: MaterialOverride):
    """
    Override element material
    """
    if override_engine is None:
        raise HTTPException(status_code=503, detail="Override engine not loaded")
    
    result = override_engine.override_material(
        element_id,
        override.new_material,
        override.user
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.post("/overrides/bulk")
def bulk_override_dimensions(bulk: BulkOverride):
    """
    Override multiple dimensions at once
    """
    if override_engine is None:
        raise HTTPException(status_code=503, detail="Override engine not loaded")
    
    return override_engine.bulk_override_dimensions(bulk.overrides, bulk.user)

@app.post("/element/{element_id}/verify")
def mark_as_verified(element_id: str, user: str = Query("system")):
    """
    Mark element as human-verified without changing dimensions
    Upgrades confidence to 1.0
    """
    if override_engine is None:
        raise HTTPException(status_code=503, detail="Override engine not loaded")
    
    result = override_engine.mark_as_verified(element_id, user)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.post("/element/{element_id}/revert")
def revert_override(element_id: str, user: str = Query("system")):
    """
    Revert element to AI-extracted values using audit trail
    """
    if override_engine is None:
        raise HTTPException(status_code=503, detail="Override engine not loaded")
    
    result = override_engine.revert_override(element_id, user)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.get("/overrides/audit")
def get_audit_log(element_id: Optional[str] = Query(None)):
    """
    Get audit log for all elements or specific element
    """
    if override_engine is None:
        raise HTTPException(status_code=503, detail="Override engine not loaded")
    
    logs = override_engine.get_audit_log(element_id)
    
    return {
        "element_id": element_id,
        "count": len(logs),
        "audit_log": logs
    }

@app.get("/overrides/summary")
def get_override_summary():
    """
    Get summary statistics of all overrides
    """
    if override_engine is None:
        raise HTTPException(status_code=503, detail="Override engine not loaded")
    
    return override_engine.get_override_summary()

@app.get("/overrides/needs-recalc")
def get_elements_needing_recalculation():
    """
    Get list of elements that need recalculation after override
    """
    if override_engine is None:
        raise HTTPException(status_code=503, detail="Override engine not loaded")
    
    element_ids = override_engine.get_elements_needing_recalculation()
    
    return {
        "count": len(element_ids),
        "element_ids": element_ids,
        "note": "These elements have been modified and need QTO recalculation (Step 3)"
    }

@app.post("/load-element-graph")
def load_element_graph(filepath: str):
    """
    Manually load element graph from file
    (For testing/development)
    """
    global element_graph, viewer, override_engine
    
    element_graph = load_element_graph_from_file(filepath)
    viewer = ElementViewer(element_graph)
    override_engine = OverrideEngine(element_graph)
    
    return {
        "message": "Element graph loaded",
        "elements_count": len(element_graph)
    }


# ============================================================================
# STEP 3: CHANGE LOG ENDPOINTS (Compliance & Traceability)
# ============================================================================

@app.get("/changelog/all")
def get_all_change_logs(limit: Optional[int] = Query(None)):
    """
    Get all change logs with optional limit
    Enterprise-grade audit trail
    """
    if change_logger is None:
        raise HTTPException(status_code=503, detail="Change logger not loaded")
    
    logs = change_logger.get_all_logs(limit)
    
    return {
        "total": len(logs),
        "logs": logs
    }

@app.get("/changelog/element/{element_id}")
def get_element_change_log(element_id: str):
    """
    Get complete change history for a specific element
    """
    if change_logger is None:
        raise HTTPException(status_code=503, detail="Change logger not loaded")
    
    logs = change_logger.get_logs_by_element(element_id)
    
    return {
        "element_id": element_id,
        "total_changes": len(logs),
        "change_history": logs
    }

@app.get("/changelog/user/{user}")
def get_user_change_log(user: str):
    """
    Get all changes made by a specific user
    """
    if change_logger is None:
        raise HTTPException(status_code=503, detail="Change logger not loaded")
    
    logs = change_logger.get_logs_by_user(user)
    
    return {
        "user": user,
        "total_changes": len(logs),
        "changes": logs
    }

@app.get("/changelog/action/{action}")
def get_logs_by_action(action: str):
    """
    Get logs by action type (override, verify, revert)
    """
    if change_logger is None:
        raise HTTPException(status_code=503, detail="Change logger not loaded")
    
    logs = change_logger.get_logs_by_action(action)
    
    return {
        "action": action,
        "total": len(logs),
        "logs": logs
    }

class ChangeLogSearch(BaseModel):
    element_id: Optional[str] = None
    edited_by: Optional[str] = None
    action: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@app.post("/changelog/search")
def search_change_logs(search: ChangeLogSearch):
    """
    Search change logs with multiple filters
    """
    if change_logger is None:
        raise HTTPException(status_code=503, detail="Change logger not loaded")
    
    filters = {k: v for k, v in search.dict().items() if v is not None}
    logs = change_logger.search_logs(filters)
    
    return {
        "filters": filters,
        "total_results": len(logs),
        "results": logs
    }

@app.get("/changelog/summary")
def get_change_summary():
    """
    Get summary statistics of all changes
    """
    if change_logger is None:
        raise HTTPException(status_code=503, detail="Change logger not loaded")
    
    return change_logger.get_change_summary()

@app.get("/changelog/export")
def export_compliance_report(format: str = Query("json", regex="^(json|csv)$")):
    """
    Export change logs for compliance reporting
    Formats: json, csv
    """
    if change_logger is None:
        raise HTTPException(status_code=503, detail="Change logger not loaded")
    
    report = change_logger.export_compliance_report(format)
    
    if format == "json":
        return {"report": json.loads(report)}
    else:
        return {"report": report, "format": "csv"}

@app.get("/changelog/integrity")
def verify_log_integrity():
    """
    Verify change log integrity (no tampering)
    """
    if change_logger is None:
        raise HTTPException(status_code=503, detail="Change logger not loaded")
    
    return change_logger.verify_log_integrity()

@app.post("/load-element-graph")
def load_element_graph(filepath: str, project_id: str = "default_project"):
    """
    Manually load element graph from file
    (For testing/development)
    """
    global element_graph, viewer, override_engine, change_logger
    
    element_graph = load_element_graph_from_file(filepath)
    
    # Initialize with project-specific change logger
    change_logger = ChangeLogger(
        storage_path=f"change_logs_{project_id}.json",
        project_id=project_id
    )
    
    viewer = ElementViewer(element_graph)
    override_engine = OverrideEngine(element_graph, change_logger)
    
    return {
        "message": "Element graph loaded",
        "elements_count": len(element_graph),
        "project_id": project_id
    }


# ============================================================================
# STEP 4: RECALCULATION ENGINE ENDPOINTS (Controlled Cascade)
# ============================================================================

@app.post("/recalculate")
def trigger_recalculation(user: str = Query("system")):
    """
    Trigger controlled cascade recalculation
    
    User-triggered, not automatic
    Recalculates: QTO → Cost → Schedule
    Clears recalculation flags
    """
    if recalculation_engine is None:
        raise HTTPException(status_code=503, detail="Recalculation engine not loaded")
    
    result = recalculation_engine.trigger_recalculation(user)
    
    return result

@app.get("/recalculate/preview")
def preview_recalculation():
    """
    Preview what would be recalculated without actually doing it
    Shows which elements will be updated
    """
    if recalculation_engine is None:
        raise HTTPException(status_code=503, detail="Recalculation engine not loaded")
    
    return recalculation_engine.preview_recalculation()

@app.get("/recalculate/status")
def get_recalculation_status():
    """
    Get recalculation status summary
    Shows how many elements need recalculation
    """
    if recalculation_engine is None:
        raise HTTPException(status_code=503, detail="Recalculation engine not loaded")
    
    return recalculation_engine.get_recalculation_summary()

@app.get("/recalculate/pending")
def get_pending_recalculations():
    """
    Get list of elements pending recalculation
    """
    if recalculation_engine is None:
        raise HTTPException(status_code=503, detail="Recalculation engine not loaded")
    
    pending = recalculation_engine.get_elements_needing_recalculation()
    
    return {
        "count": len(pending),
        "element_ids": pending,
        "note": "These elements have been modified and need recalculation"
    }

@app.post("/load-element-graph")
def load_element_graph(filepath: str, project_id: str = "default_project"):
    """
    Manually load element graph from file
    (For testing/development)
    """
    global element_graph, viewer, override_engine, change_logger, recalculation_engine, approval_engine, qto_summary
    
    element_graph = load_element_graph_from_file(filepath)
    
    # Initialize with project-specific change logger
    change_logger = ChangeLogger(
        storage_path=f"change_logs_{project_id}.json",
        project_id=project_id
    )
    
    # Initialize QTO summary (in production, this comes from Layer 4-6)
    qto_summary = {
        "Concrete in Slab": {
            "quantity": 12.45,
            "cost": 85600,
            "status": "Pending"
        },
        "Brickwork": {
            "quantity": 8.23,
            "cost": 34200,
            "status": "Approved"
        }
    }
    
    # Initialize recalculation engines with configurable rates/productivity
    qto_engine = QTOEngine(element_graph)
    cost_engine = CostEngine(element_graph, rate_table={"RCC": 7000, "Brick": 5000})
    schedule_engine = ScheduleEngine(element_graph, productivity_table={"Wall": 5, "Slab": 10, "Column": 3})
    
    # Initialize approval engine
    approval_engine = ApprovalEngine(qto_summary)
    
    viewer = ElementViewer(element_graph)
    override_engine = OverrideEngine(element_graph, change_logger)
    recalculation_engine = RecalculationEngine(element_graph, qto_engine, cost_engine, schedule_engine, approval_engine)
    
    return {
        "message": "Element graph loaded",
        "elements_count": len(element_graph),
        "project_id": project_id
    }


# ============================================================================
# STEP 5: APPROVAL STATUS SYSTEM ENDPOINTS (Final Governance Lock)
# ============================================================================

class StatusUpdate(BaseModel):
    status: str

class BulkApproval(BaseModel):
    item_names: List[str]

@app.post("/qto/{item_name}/approve")
def approve_item(item_name: str):
    """
    Approve a QTO item
    Marks item as ready for export
    """
    if approval_engine is None:
        raise HTTPException(status_code=503, detail="Approval engine not loaded")
    
    result = approval_engine.approve_item(item_name)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.post("/qto/{item_name}/reject")
def reject_item(item_name: str):
    """
    Reject a QTO item
    Flags item as incorrect
    """
    if approval_engine is None:
        raise HTTPException(status_code=503, detail="Approval engine not loaded")
    
    result = approval_engine.reject_item(item_name)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.post("/qto/{item_name}/status")
def set_item_status(item_name: str, status_update: StatusUpdate):
    """
    Set custom status for a QTO item
    Allowed: Pending, Approved, Rejected, Needs Review
    """
    if approval_engine is None:
        raise HTTPException(status_code=503, detail="Approval engine not loaded")
    
    result = approval_engine.set_status(item_name, status_update.status)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@app.post("/qto/bulk-approve")
def bulk_approve_items(bulk: BulkApproval):
    """
    Approve multiple QTO items at once
    """
    if approval_engine is None:
        raise HTTPException(status_code=503, detail="Approval engine not loaded")
    
    return approval_engine.bulk_approve(bulk.item_names)

@app.get("/qto/unapproved")
def get_unapproved():
    """
    Get all unapproved QTO items
    These items cannot be exported
    """
    if approval_engine is None:
        raise HTTPException(status_code=503, detail="Approval engine not loaded")
    
    unapproved = approval_engine.get_unapproved_items()
    
    return {
        "count": len(unapproved),
        "items": unapproved
    }

@app.get("/qto/status/{status}")
def get_items_by_status(status: str):
    """
    Get all QTO items with a specific status
    """
    if approval_engine is None:
        raise HTTPException(status_code=503, detail="Approval engine not loaded")
    
    result = approval_engine.get_items_by_status(status)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "status": status,
        "count": len(result),
        "items": result
    }

@app.get("/qto/approval-summary")
def get_approval_summary():
    """
    Get summary of approval statuses
    Shows counts by status and export readiness
    """
    if approval_engine is None:
        raise HTTPException(status_code=503, detail="Approval engine not loaded")
    
    return approval_engine.get_approval_summary()

@app.get("/qto/can-export")
def check_export_readiness():
    """
    Check if QTO can be exported
    Returns true only if all items are approved
    """
    if approval_engine is None:
        raise HTTPException(status_code=503, detail="Approval engine not loaded")
    
    return approval_engine.can_export()
