from datetime import datetime

from beanie import Document
from models.event import EventRequest
from pydantic import BaseModel, Field


class RoutingResult(BaseModel):
    destination_name: str
    routed: bool
    error: str | None = None


class EventLog(Document):
    timestamp: datetime = Field(default_factory=datetime.now)
    request: EventRequest
    response: list[RoutingResult]

    class Settings:
        name = 'event_logs'
