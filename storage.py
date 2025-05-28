from typing import List
from models import HandoverNote

# In-memory DB (can be replaced with SQLite or Firebase for persistence)
notes_db: List[HandoverNote] = []
