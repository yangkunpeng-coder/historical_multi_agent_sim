import logging
from datetime import datetime, timedelta, timezone

from activity.activity import Activity, ActivityType
from activity.activity_manager import ActivityManager
from agents.agent import HistoricalAgent
from agents.memory import MemoryItem
from agents.perception import Perception
from agents.profile import AgentProfile
from agents.registry import AgentRegistry
from agents.state import AgentState
from config.constants import EventPriority, EventType
from config.settings import Settings
from core.clock import SimulationClock
from core.event import Event
from core.event_queue import EventQueue
from core.scheduler import Scheduler
from core.simulation_engine import SimulationEngine
from core.world import AudienceType, World
from planning.goal import Goal
from planning.plan import Plan, Task
from reasoning.deepseek_client import DeepSeekClient
from reasoning.react_engine import ReActEngine, historical_fallback_policy
from scenarios.base import Scenario, ScenarioRuntime
from social.update_policy import RelationshipUpdatePolicy
from spatial.location import Location, LocationKind
from spatial.movement import MovementService
from storage.event_store import EventStore, InMemoryEventStore
from tools.base import ToolContext
from tools.registry import ToolRegistry
from tools.social_tools import MoveToTool, SendLetterTool, SocializeTool, StudyTool

CHINA_TZ = timezone(timedelta(hours=8))


class CountyExamScenario(Scenario):
    """A compact late-Qing county exam preparation scenario."""

    def __init__(
        self,
        settings: Settings | None = None,
        event_store: EventStore | None = None,
    ) -> None:
        self.settings = settings or Settings.from_env()
        self.event_store = event_store or InMemoryEventStore()
        self.logger = logging.getLogger(__name__)
        self.relationship_policy = RelationshipUpdatePolicy()

    def build(self) -> ScenarioRuntime:
        clock = SimulationClock(datetime(1850, 3, 10, 8, 0, tzinfo=CHINA_TZ))
        queue = EventQueue()
        scheduler = Scheduler(clock, queue)
        world = self._build_world()
        movement = MovementService(
            {
                ("li_home", "academy"): 30,
                ("li_home", "exam_hall"): 90,
                ("academy", "exam_hall"): 60,
            }
        )
        tools = ToolRegistry()
        for tool in (SendLetterTool(), MoveToTool(), StudyTool(), SocializeTool()):
            tools.register(tool)
        react = ReActEngine(
            DeepSeekClient(self.settings),
            tools,
            historical_fallback_policy,
        )
        for agent in world.agents.all():
            agent.react_engine = react

        engine = SimulationEngine(clock, queue, self.event_store)
        self._register_handlers(engine, scheduler, world, movement)
        self._schedule_opening(scheduler)
        return ScenarioRuntime(engine=engine, world=world)

    def _build_world(self) -> World:
        registry = AgentRegistry()
        scholar = HistoricalAgent(
            AgentProfile(
                agent_id="li_ming",
                name="李明",
                age=19,
                role="scholar",
                background="江南县城寒门生员之子，准备参加县试。",
                traits=["勤勉", "谨慎"],
            ),
            AgentState(location_id="li_home", money=8, knowledge=6),
        )
        teacher = HistoricalAgent(
            AgentProfile(
                agent_id="teacher_wang",
                name="王先生",
                age=52,
                role="teacher",
                background="本地塾师。",
                traits=["严谨"],
            ),
            AgentState(location_id="academy", money=30, knowledge=80),
        )
        scholar.goals.add(
            Goal(
                goal_id="pass_county_exam",
                description="通过本年度县试",
                priority=95,
                long_term=True,
            )
        )
        scholar.plans.add(
            Plan(
                plan_id="county_exam_plan",
                goal_id="pass_county_exam",
                tasks=[
                    Task(
                        task_id="review_classics",
                        description="温习经义",
                        action_name="study",
                        priority=90,
                    ),
                    Task(
                        task_id="travel_to_exam",
                        description="赴考院应试",
                        action_name="move_to",
                        action_arguments={"destination_id": "exam_hall"},
                        dependencies={"review_classics"},
                        priority=80,
                    ),
                ],
            )
        )
        registry.add(scholar)
        registry.add(teacher)
        world = World(registry)
        for location in (
            Location(location_id="li_home", name="李家", kind=LocationKind.HOME, capacity=8),
            Location(location_id="academy", name="王氏私塾", kind=LocationKind.VILLAGE, capacity=30),
            Location(location_id="exam_hall", name="江宁县考院", kind=LocationKind.EXAM_HALL, capacity=500),
        ):
            world.add_location(location)
        return world

    def _schedule_opening(self, scheduler: Scheduler) -> None:
        scheduler.schedule(
            EventType.ENVIRONMENT,
            priority=EventPriority.HIGH,
            payload={
                "audience": AudienceType.ROLE,
                "audience_value": "scholar",
                "perception_type": "exam_announced",
                "description": "县衙张榜：三日后举行县试。",
                "importance": 90,
            },
        )

    def _register_handlers(
        self,
        engine: SimulationEngine,
        scheduler: Scheduler,
        world: World,
        movement: MovementService,
    ) -> None:
        engine.register_handler(EventType.ENVIRONMENT, lambda event: self._environment(event, scheduler, world))
        engine.register_handler(EventType.PERCEPTION, lambda event: self._perception(event, scheduler, world))
        engine.register_handler(
            EventType.AGENT_DECISION,
            lambda event: self._decision(event, scheduler, world, movement),
        )
        engine.register_handler(EventType.ACTIVITY_START, lambda event: self._activity_start(event, scheduler, world))
        engine.register_handler(EventType.ACTIVITY_FINISH, lambda event: self._activity_finish(event, scheduler, world))
        engine.register_handler(
            EventType.MOVEMENT_STARTED,
            lambda event: self._movement_started(event, scheduler, world),
        )
        engine.register_handler(EventType.ARRIVAL, lambda event: self._arrival(event, world))
        engine.register_handler(EventType.LETTER_CREATED, lambda event: self._letter_created(event, scheduler))
        engine.register_handler(EventType.LETTER_DELIVERED, lambda event: self._letter_delivered(event, world))
        engine.register_handler(EventType.SOCIAL_INTERACTION, lambda event: self._social(event, world))

    def _environment(self, event: Event, scheduler: Scheduler, world: World) -> None:
        audience = AudienceType(event.payload["audience"])
        recipients = world.resolve_recipients(audience, value=event.payload.get("audience_value"))
        for agent_id in recipients:
            scheduler.schedule(
                EventType.PERCEPTION,
                priority=EventPriority.HIGH,
                sender_id=event.sender_id,
                receiver_id=agent_id,
                payload={
                    "event_type": event.payload["perception_type"],
                    "description": event.payload["description"],
                    "data": event.payload.get("data", {}),
                    "importance": event.payload.get("importance", 50),
                },
            )

    def _perception(self, event: Event, scheduler: Scheduler, world: World) -> None:
        if event.receiver_id is None:
            raise ValueError("Perception requires a receiver")
        agent = world.agents.get(event.receiver_id)
        perception = Perception(
            event_type=event.payload["event_type"],
            description=event.payload["description"],
            source_id=event.sender_id,
            data=event.payload.get("data", {}),
        )
        agent.memory.add(
            MemoryItem(
                timestamp=scheduler.now,
                content=perception.description,
                importance=event.payload.get("importance", 50),
                metadata={"event_type": perception.event_type},
            )
        )
        scheduler.schedule(
            EventType.AGENT_DECISION,
            receiver_id=agent.agent_id,
            payload=perception.model_dump(mode="json"),
            priority=EventPriority.NORMAL,
        )

    def _decision(
        self,
        event: Event,
        scheduler: Scheduler,
        world: World,
        movement: MovementService,
    ) -> None:
        if event.receiver_id is None:
            raise ValueError("Decision requires a receiver")
        agent = world.agents.get(event.receiver_id)
        if agent.react_engine is None:
            raise RuntimeError("Agent has no ReAct engine")
        perception = Perception.model_validate(event.payload)
        decision, result = agent.react_engine.act(
            agent,
            perception,
            ToolContext(agent.agent_id, world, scheduler, movement),
        )
        event.payload["decision"] = decision.model_dump(mode="json")
        if result is not None:
            event.payload["tool_result"] = {
                "success": result.success,
                "message": result.message,
                "event_ids": result.event_ids,
            }

    def _activity_start(self, event: Event, scheduler: Scheduler, world: World) -> None:
        if event.receiver_id is None:
            raise ValueError("Activity requires a receiver")
        agent = world.agents.get(event.receiver_id)
        if not agent.state.available:
            raise RuntimeError(f"Agent {agent.agent_id} is busy")
        activity = Activity.model_validate(event.payload)
        agent.state.available = False
        agent.state.current_activity = activity.activity_type
        scheduler.schedule(
            EventType.ACTIVITY_FINISH,
            delay=timedelta(minutes=activity.duration_minutes),
            receiver_id=agent.agent_id,
            payload=activity.model_dump(mode="json"),
        )

    def _activity_finish(self, event: Event, scheduler: Scheduler, world: World) -> None:
        if event.receiver_id is None:
            raise ValueError("Activity requires a receiver")
        agent = world.agents.get(event.receiver_id)
        activity = Activity.model_validate(event.payload)
        for field, change in ActivityManager.effects(activity.activity_type).items():
            current = getattr(agent.state, field)
            upper = 100 if field in {"energy", "knowledge"} else None
            updated = max(0, current + change)
            setattr(agent.state, field, min(upper, updated) if upper is not None else updated)
        agent.state.available = True
        agent.state.current_activity = None
        if activity.activity_type == ActivityType.STUDY:
            try:
                agent.plans.mark("review_classics", "completed")
            except KeyError:
                pass
            scheduler.schedule(
                EventType.PERCEPTION,
                receiver_id=agent.agent_id,
                payload={
                    "event_type": "study_completed",
                    "description": f"{activity.description}已完成。",
                    "importance": 60,
                    "data": {},
                },
            )

    def _movement_started(self, event: Event, scheduler: Scheduler, world: World) -> None:
        if event.receiver_id is None:
            raise ValueError("Movement requires a receiver")
        agent = world.agents.get(event.receiver_id)
        if not agent.state.available:
            raise RuntimeError(f"Agent {agent.agent_id} is busy")
        agent.state.available = False
        agent.state.current_activity = ActivityType.TRAVEL
        scheduler.schedule(
            EventType.ARRIVAL,
            delay=timedelta(minutes=event.payload["duration_minutes"]),
            receiver_id=agent.agent_id,
            payload={"destination_id": event.payload["destination_id"]},
            priority=EventPriority.HIGH,
        )

    def _arrival(self, event: Event, world: World) -> None:
        if event.receiver_id is None:
            raise ValueError("Arrival requires a receiver")
        world.move_agent(event.receiver_id, event.payload["destination_id"])
        agent = world.agents.get(event.receiver_id)
        agent.state.available = True
        agent.state.current_activity = None
        try:
            agent.plans.mark("travel_to_exam", "completed")
        except KeyError:
            pass

    def _letter_created(self, event: Event, scheduler: Scheduler) -> None:
        scheduler.schedule(
            EventType.LETTER_DELIVERED,
            delay=timedelta(hours=2),
            sender_id=event.sender_id,
            receiver_id=event.receiver_id,
            payload=event.payload,
        )

    def _letter_delivered(self, event: Event, world: World) -> None:
        if event.receiver_id is None or event.sender_id is None:
            raise ValueError("Letter requires sender and receiver")
        receiver = world.agents.get(event.receiver_id)
        receiver.memory.add(
            MemoryItem(
                timestamp=event.trigger_time,
                content=f"收到书信：{event.payload['content']}",
                importance=55,
                metadata={"sender_id": event.sender_id},
            )
        )
        self.relationship_policy.apply(receiver.relationships.get(event.sender_id), "letter")

    def _social(self, event: Event, world: World) -> None:
        if event.receiver_id is None or event.sender_id is None:
            raise ValueError("Social interaction requires two agents")
        interaction = event.payload.get("interaction", "conversation")
        source = world.agents.get(event.sender_id)
        target = world.agents.get(event.receiver_id)
        self.relationship_policy.apply(source.relationships.get(target.agent_id), interaction)
        self.relationship_policy.apply(target.relationships.get(source.agent_id), interaction)

