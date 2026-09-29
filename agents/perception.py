from typing import Any

from pydantic import BaseModel, Field


class Perception(BaseModel):
    event_type: str
    description: str
    source_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)

