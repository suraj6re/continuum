from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional

class Drawing(Document):
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    file_path: str
    project_id: Optional[str] = None
    status: str = "uploaded"
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "drawings"
