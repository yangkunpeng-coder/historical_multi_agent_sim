import unittest
from datetime import datetime, timedelta, timezone

from core.clock import SimulationClock
from core.event import EventStatus
from core.event_queue import EventQueue
from core.scheduler import Scheduler
from core.simulation_engine import SimulationEngine
from storage.event_store import InMemoryEventStore


class EventCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime(1850, 1, 1, tzinfo=timezone.utc)
        self.clock = SimulationClock(self.start)
        self.queue = EventQueue()
        self.scheduler = Scheduler(self.clock, self.queue)

    def test_queue_orders_by_time_then_priority(self) -> None:
        late = self.scheduler.schedule("test", delay=timedelta(hours=1), priority=0)
        low = self.scheduler.schedule("test", priority=75)
        high = self.scheduler.schedule("test", priority=25)
        self.assertEqual(self.queue.pop().event_id, high.event_id)
        self.assertEqual(self.queue.pop().event_id, low.event_id)
        self.assertEqual(self.queue.pop().event_id, late.event_id)

    def test_queue_has_no_public_push(self) -> None:
        self.assertFalse(hasattr(self.queue, "push"))

    def test_engine_persists_failure_and_continues(self) -> None:
        store = InMemoryEventStore()
        engine = SimulationEngine(self.clock, self.queue, store)
        seen: list[str] = []

        def handler(event) -> None:
            if event.payload.get("fail"):
                raise RuntimeError("boom")
            seen.append(event.event_id)

        engine.register_handler("test", handler)
        self.scheduler.schedule("test", payload={"fail": True})
        ok = self.scheduler.schedule("test")
        count = engine.run()
        self.assertEqual(count, 2)
        self.assertEqual(seen, [ok.event_id])
        self.assertEqual(store.events[0].status, EventStatus.FAILED)
        self.assertEqual(store.events[1].status, EventStatus.EXECUTED)

    def test_cannot_schedule_in_past(self) -> None:
        with self.assertRaises(ValueError):
            self.scheduler.schedule("test", trigger_time=self.start - timedelta(seconds=1))


if __name__ == "__main__":
    unittest.main()

