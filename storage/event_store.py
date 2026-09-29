import json
from pathlib import Path
from threading import Lock

from core.event import Event


class EventStore:
    def append(self, event: Event) -> None:
        raise NotImplementedError


class InMemoryEventStore(EventStore):
    def __init__(self) -> None:
        self.events: list[Event] = []

    def append(self, event: Event) -> None:
        self.events.append(event.model_copy(deep=True))


class JsonlEventStore(EventStore):
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = Lock()

    def append(self, event: Event) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event.model_dump(mode="json"), ensure_ascii=False)
        with self._lock, self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

