from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventStatus(StrEnum):
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Event(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    event_id: str
    event_type: str
    trigger_time: datetime
    priority: int = Field(ge=0, le=100)
    sender_id: str | None = None
    receiver_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    status: EventStatus = EventStatus.PENDING
    error: str | None = None

