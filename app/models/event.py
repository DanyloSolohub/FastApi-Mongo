from enum import Enum
from typing import Any

from beanie import Document, Link
from pydantic import BaseModel


class RoutingIntent(BaseModel):
    destination_name: str
    important: bool = False
    bytes: int = 0
    score: int | None = None


class RoutingIntentRequest(BaseModel):
    destination_name: str
    important: bool = False
    score: int | None = None


class StrategyEnum(str, Enum):
    ALL = 'ALL'
    IMPORTANT = 'IMPORTANT'
    SMALL = 'SMALL'


class Strategy(Document):
    name: StrategyEnum
    custom_code: str | None = None
    is_default: bool = False
    is_client_strategy: bool = False

    class Settings:
        name = 'strategies'


class Event(Document):
    payload: dict[str, Any]
    routing_intents: list[RoutingIntent]
    strategy: Link['Strategy'] | None = None

    class Settings:
        name = 'events'


class EventRequest(BaseModel):
    payload: dict[str, Any]
    routing_intents: list[RoutingIntentRequest]
    strategy: str | None = None
