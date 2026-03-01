import json
from datetime import datetime
import os

LOG_FILE = "communication_logs.json"

def log_communication(
    supplier,
    material,
    quantity,
    unit,
    mode,
    status="Drafted",
    project_name=None,
    expected_rate=None
):
    """
    Log communication attempt with supplier
    
    Args:
        supplier: Supplier name
        material: Material description
        quantity: Quantity required
        unit: Unit of measurement
        mode: Communication mode (RFQ/WhatsApp/Email)
        status: Status (Drafted/Sent/Delivered/Failed)
        project_name: Project name (optional)
        expected_rate: Expected rate (optional)
    
    Returns:
        Log entry dictionary
    """
    log_entry = {
        "log_id": f"LOG-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "supplier": supplier,
        "material": material,
        "quantity": quantity,
        "unit": unit,
        "mode": mode,
        "status": status,
        "project_name": project_name,
        "expected_rate": expected_rate
    }
    
    # Load existing logs or create new list
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []
    
    # Append new log
    data.append(log_entry)
    
    # Save logs
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)
    
    return log_entry


def get_logs(supplier=None, mode=None, limit=None):
    """
    Retrieve communication logs with optional filters
    
    Args:
        supplier: Filter by supplier name (optional)
        mode: Filter by communication mode (optional)
        limit: Limit number of results (optional)
    
    Returns:
        List of log entries
    """
    if not os.path.exists(LOG_FILE):
        return []
    
    with open(LOG_FILE, "r") as f:
        data = json.load(f)
    
    # Apply filters
    if supplier:
        data = [log for log in data if log["supplier"].lower() == supplier.lower()]
    
    if mode:
        data = [log for log in data if log["mode"].lower() == mode.lower()]
    
    # Apply limit
    if limit:
        data = data[-limit:]
    
    return data


def get_log_summary():
    """
    Get summary statistics of communication logs
    
    Returns:
        Dictionary with summary statistics
    """
    if not os.path.exists(LOG_FILE):
        return {
            "total_logs": 0,
            "by_mode": {},
            "by_status": {},
            "unique_suppliers": 0
        }
    
    with open(LOG_FILE, "r") as f:
        data = json.load(f)
    
    # Calculate statistics
    by_mode = {}
    by_status = {}
    suppliers = set()
    
    for log in data:
        # Count by mode
        mode = log["mode"]
        by_mode[mode] = by_mode.get(mode, 0) + 1
        
        # Count by status
        status = log["status"]
        by_status[status] = by_status.get(status, 0) + 1
        
        # Track unique suppliers
        suppliers.add(log["supplier"])
    
    return {
        "total_logs": len(data),
        "by_mode": by_mode,
        "by_status": by_status,
        "unique_suppliers": len(suppliers)
    }
