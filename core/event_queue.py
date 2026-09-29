import heapq
from itertools import count

from core.event import Event


class EventQueue:
    """Priority queue. Scheduler is the only intended writer via _push."""

    def __init__(self) -> None:
        self._heap: list[tuple[float, int, int, Event]] = []
        self._sequence = count()

    def _push(self, event: Event) -> None:
        heapq.heappush(
            self._heap,
            (event.trigger_time.timestamp(), event.priority, next(self._sequence), event),
        )

    def pop(self) -> Event:
        if not self._heap:
            raise IndexError("Cannot pop from an empty event queue")
        return heapq.heappop(self._heap)[3]

    def peek(self) -> Event | None:
        return self._heap[0][3] if self._heap else None

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return bool(self._heap)

