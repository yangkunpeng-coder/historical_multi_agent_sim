from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    timestamp: datetime
    content: str
    importance: int = Field(default=50, ge=0, le=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Memory:
    def __init__(self, capacity: int = 200) -> None:
        if capacity < 1:
            raise ValueError("Memory capacity must be positive")
        self.capacity = capacity
        self._items: list[MemoryItem] = []

    def add(self, item: MemoryItem) -> None:
        self._items.append(item)
        if len(self._items) > self.capacity:
            self._items.sort(key=lambda value: (value.importance, value.timestamp))
            self._items.pop(0)

    def recent(self, limit: int = 10) -> list[MemoryItem]:
        return sorted(self._items, key=lambda item: item.timestamp, reverse=True)[:limit]

    def __len__(self) -> int:
        return len(self._items)

