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
    
    class Settings:
        name = "drawings"
