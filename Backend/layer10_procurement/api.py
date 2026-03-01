from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from rfq_generator import generate_rfq, generate_rfq_payload
from whatsapp_template import generate_whatsapp, generate_whatsapp_payload
from communication_logger import log_communication, get_logs, get_log_summary

app = FastAPI(title="Layer 10 - Procurement Agent API")

class RFQRequest(BaseModel):
    supplier_name: str
    material: str
    quantity: float
    unit: str
    project_name: str
    delivery_date: Optional[str] = None
    supplier_id: Optional[int] = None
    supplier_location: Optional[str] = None
    expected_rate: Optional[float] = None
    distance_km: Optional[int] = None
    lead_time_days: Optional[int] = None

class Layer8Layer9Input(BaseModel):
    """Combined input from Layer 8 and Layer 9"""
    layer8: dict  # {description, quantity, unit}
    layer9: dict  # {recommended_supplier, best_rate, etc.}
    project_name: str
    delivery_date: Optional[str] = None

@app.post("/generate_rfq")
def generate_rfq_endpoint(request: RFQRequest):
    """Generate RFQ from direct input"""
    payload = generate_rfq_payload(
        supplier_name=request.supplier_name,
        supplier_id=request.supplier_id,
        supplier_location=request.supplier_location,
        material=request.material,
        quantity=request.quantity,
        unit=request.unit,
        project_name=request.project_name,
        delivery_date=request.delivery_date,
        expected_rate=request.expected_rate,
        distance_km=request.distance_km,
        lead_time_days=request.lead_time_days
    )
    return payload

@app.post("/generate_rfq_from_layers")
def generate_rfq_from_layers(request: Layer8Layer9Input):
    """Generate RFQ from Layer 8 and Layer 9 outputs"""
    layer8 = request.layer8
    layer9 = request.layer9
    
    # Extract supplier location from comparison if available
    supplier_location = None
    if "comparison" in layer9 and len(layer9["comparison"]) > 0:
        supplier_location = layer9["comparison"][0].get("location")
    
    payload = generate_rfq_payload(
        supplier_name=layer9.get("recommended_supplier"),
        supplier_id=layer9.get("recommended_supplier_id"),
        supplier_location=supplier_location,
        material=layer8.get("description"),
        quantity=layer8.get("quantity"),
        unit=layer8.get("unit"),
        project_name=request.project_name,
        delivery_date=request.delivery_date,
        expected_rate=layer9.get("best_rate"),
        distance_km=layer9.get("best_distance"),
        lead_time_days=layer9.get("best_lead_time")
    )
    
    return payload

@app.get("/")
def root():
    return {
        "message": "Layer 10 - Procurement Agent API",
        "endpoints": {
            "/generate_rfq": "Generate RFQ from direct input",
            "/generate_rfq_from_layers": "Generate RFQ from Layer 8 & 9 outputs",
            "/generate_whatsapp": "Generate WhatsApp message",
            "/log_communication": "Log communication attempt",
            "/get_logs": "Retrieve communication logs",
            "/get_log_summary": "Get log statistics"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy", "layer": 10, "steps": [1, 2, 3]}


# WhatsApp Endpoints

class WhatsAppRequest(BaseModel):
    supplier_name: str
    material: str
    quantity: float
    unit: str
    project_name: str
    expected_rate: Optional[float] = None
    supplier_phone: Optional[str] = None

@app.post("/generate_whatsapp")
def generate_whatsapp_endpoint(request: WhatsAppRequest):
    """Generate WhatsApp message"""
    payload = generate_whatsapp_payload(
        supplier_name=request.supplier_name,
        material=request.material,
        quantity=request.quantity,
        unit=request.unit,
        project_name=request.project_name,
        expected_rate=request.expected_rate,
        supplier_phone=request.supplier_phone
    )
    return payload


# Communication Logging Endpoints

class LogRequest(BaseModel):
    supplier: str
    material: str
    quantity: float
    unit: str
    mode: str  # RFQ/WhatsApp/Email
    status: Optional[str] = "Drafted"
    project_name: Optional[str] = None
    expected_rate: Optional[float] = None

@app.post("/log_communication")
def log_communication_endpoint(request: LogRequest):
    """Log communication attempt"""
    log_entry = log_communication(
        supplier=request.supplier,
        material=request.material,
        quantity=request.quantity,
        unit=request.unit,
        mode=request.mode,
        status=request.status,
        project_name=request.project_name,
        expected_rate=request.expected_rate
    )
    return log_entry

@app.get("/get_logs")
def get_logs_endpoint(supplier: Optional[str] = None, mode: Optional[str] = None, limit: Optional[int] = None):
    """Retrieve communication logs with optional filters"""
    logs = get_logs(supplier=supplier, mode=mode, limit=limit)
    return {"logs": logs, "count": len(logs)}

@app.get("/get_log_summary")
def get_log_summary_endpoint():
    """Get summary statistics of communication logs"""
    summary = get_log_summary()
    return summary
