from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
import uuid

class Message(Document):
    sender_id: uuid.UUID
    sender_name: str
    text: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "messages"
        indexes = [
            [("created_at", 1)],
            [("sender_id", 1)],
        ]