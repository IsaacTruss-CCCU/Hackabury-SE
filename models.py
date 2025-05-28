from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HandoverNote(BaseModel):
    id: str
    text: str                 # The main note text
    station_code: Optional[str] = None  # The station code (optional)
    category: str
    priority: bool
    timestamp: datetime
