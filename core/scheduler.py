from datetime import datetime, timedelta
from uuid import uuid4

from config.constants import EventPriority
from core.clock import SimulationClock
from core.event import Event
from core.event_queue import EventQueue


class Scheduler:
    def __init__(self, clock: SimulationClock, queue: EventQueue) -> None:
        self._clock = clock
        self._queue = queue

    @property
    def now(self) -> datetime:
        return self._clock.now

    def schedule(
        self,
        event_type: str,
        *,
        trigger_time: datetime | None = None,
        delay: timedelta | None = None,
        priority: int = EventPriority.NORMAL,
        sender_id: str | None = None,
        receiver_id: str | None = None,
        payload: dict | None = None,
    ) -> Event:
        if trigger_time is not None and delay is not None:
            raise ValueError("Use either trigger_time or delay, not both")
        when = trigger_time or self._clock.after(delay or timedelta(0))
        if when < self._clock.now:
            raise ValueError("Cannot schedule an event in the past")
        event = Event(
            event_id=str(uuid4()),
            event_type=event_type,
            trigger_time=when,
            priority=int(priority),
            sender_id=sender_id,
            receiver_id=receiver_id,
            payload=payload or {},
        )
        self._queue._push(event)
        return event
