from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import List, Optional

class Project(Document):
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    drawing_ids: List[str] = []
    
    class Settings:
        name = "projects"
