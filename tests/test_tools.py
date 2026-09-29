import unittest
from datetime import datetime, timezone

from agents.agent import HistoricalAgent
from agents.profile import AgentProfile
from agents.registry import AgentRegistry
from agents.state import AgentState
from core.clock import SimulationClock
from core.event_queue import EventQueue
from core.scheduler import Scheduler
from core.world import World
from spatial.location import Location, LocationKind
from spatial.movement import MovementService
from tools.base import ToolContext
from tools.social_tools import MoveToTool


class ToolBoundaryTests(unittest.TestCase):
    def test_move_tool_schedules_but_does_not_mutate_world(self) -> None:
        agent = HistoricalAgent(
            AgentProfile(agent_id="a", name="甲", age=20, role="scholar"),
            AgentState(location_id="home"),
        )
        registry = AgentRegistry()
        registry.add(agent)
        world = World(registry)
        world.add_location(Location(location_id="home", name="家", kind=LocationKind.HOME))
        world.add_location(Location(location_id="market", name="市", kind=LocationKind.MARKET))
        queue = EventQueue()
        scheduler = Scheduler(SimulationClock(datetime.now(timezone.utc)), queue)
        context = ToolContext("a", world, scheduler, MovementService({("home", "market"): 10}))
        result = MoveToTool().execute(context, {"destination_id": "market"})
        self.assertTrue(result.success)
        self.assertEqual(agent.state.location_id, "home")
        self.assertEqual(len(queue), 1)


if __name__ == "__main__":
    unittest.main()

