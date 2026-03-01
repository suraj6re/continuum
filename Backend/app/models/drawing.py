from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional, Dict, Any

class Drawing(Document):
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    file_path: str
    project_id: Optional[str] = None
    status: str = "uploaded"
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Layer 1 processing results
    processed: bool = False
    processing_error: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    # Layer 1 output
    geometry: Optional[Dict[str, Any]] = None
    bounding_box: Optional[Dict[str, float]] = None
    text: Optional[list] = None
    scale_candidates: Optional[list] = None
    units: Optional[Dict[str, Any]] = None
    layers: Optional[list] = None
    blocks: Optional[list] = None
    pipeline_type: Optional[str] = None
    entity_count: Optional[Dict[str, int]] = None
    intermediate_json: Optional[str] = None
    
    # Layer 2 output
    layer2_processed: bool = False
    layer2_data: Optional[Dict[str, Any]] = None
    
    # Layer 3 output
    layer3_processed: bool = False
    layer3_data: Optional[Dict[str, Any]] = None
    
    # Layer 4 output (QTO)
    layer4_processed: bool = False
    layer4_data: Optional[Dict[str, Any]] = None
    
    # Layer 5 output (Canonical Model)
    layer5_processed: bool = False
    layer5_data: Optional[Dict[str, Any]] = None
    
    # Layer 6 output (Validation & Confidence)
    layer6_processed: bool = False
    layer6_data: Optional[Dict[str, Any]] = None
    
    # Layer 7 output (Cost & Risk Engine)
    layer7_processed: bool = False
    layer7_data: Optional[Dict[str, Any]] = None
    
    # Layer 8 output (Supplier Discovery / Budget Optimization)
    layer8_processed: bool = False
    layer8_data: Optional[Dict[str, Any]] = None
    
    # Layer 9 output (Procurement)
    layer9_processed: bool = False
    layer9_data: Optional[Dict[str, Any]] = None
    
    # Layer 10 output (Scheduling)
    layer10_processed: bool = False
    layer10_data: Optional[Dict[str, Any]] = None
    
    class Settings:
        name = "drawings"
