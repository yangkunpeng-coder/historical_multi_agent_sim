import logging
from collections.abc import Callable

from config.constants import DEFAULT_EVENT_LIMIT
from core.clock import SimulationClock
from core.event import Event, EventStatus
from core.event_queue import EventQueue
from storage.event_store import EventStore, InMemoryEventStore

EventHandler = Callable[[Event], None]


class SimulationEngine:
    def __init__(
        self,
        clock: SimulationClock,
        queue: EventQueue,
        event_store: EventStore | None = None,
    ) -> None:
        self.clock = clock
        self.queue = queue
        self.event_store = event_store or InMemoryEventStore()
        self._handlers: dict[str, EventHandler] = {}
        self._running = False
        self.logger = logging.getLogger(__name__)

    def register_handler(self, event_type: str, handler: EventHandler) -> None:
        if event_type in self._handlers:
            raise ValueError(f"Handler already registered for {event_type}")
        self._handlers[event_type] = handler

    def run(self, *, max_events: int = DEFAULT_EVENT_LIMIT) -> int:
        self._running = True
        processed = 0
        while self._running and self.queue and processed < max_events:
            event = self.queue.pop()
            if event.status == EventStatus.CANCELLED:
                self.event_store.append(event)
                continue
            try:
                self.clock.advance_to(event.trigger_time)
                handler = self._handlers.get(event.event_type)
                if handler is None:
                    raise LookupError(f"No handler for event type: {event.event_type}")
                handler(event)
                event.status = EventStatus.EXECUTED
            except Exception as exc:  # event loop must remain alive
                event.status = EventStatus.FAILED
                event.error = f"{type(exc).__name__}: {exc}"
                self.logger.exception("Event %s failed", event.event_id)
            finally:
                self.event_store.append(event)
                processed += 1
        return processed

    def stop(self) -> None:
        self._running = False

