import unittest

from config.settings import Settings
from scenarios.county_exam import CountyExamScenario
from storage.event_store import InMemoryEventStore


class CountyExamScenarioTests(unittest.TestCase):
    def test_offline_scenario_reaches_exam_hall(self) -> None:
        store = InMemoryEventStore()
        runtime = CountyExamScenario(Settings(), store).build()
        processed = runtime.engine.run(max_events=50)
        scholar = runtime.world.agents.get("li_ming")
        self.assertGreaterEqual(processed, 8)
        self.assertEqual(scholar.state.location_id, "exam_hall")
        self.assertEqual(scholar.state.knowledge, 10)
        self.assertTrue(scholar.plans.all()[0].completed)
        self.assertFalse(any(event.error for event in store.events))


if __name__ == "__main__":
    unittest.main()

