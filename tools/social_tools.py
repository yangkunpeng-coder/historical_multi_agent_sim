from datetime import timedelta

from pydantic import BaseModel, Field, ValidationError

from activity.activity import Activity, ActivityType
from config.constants import EventPriority, EventType
from tools.base import Tool, ToolContext, ToolResult


class LetterArguments(BaseModel):
    target_id: str
    content: str = Field(min_length=1, max_length=1_000)


class MoveArguments(BaseModel):
    destination_id: str


class StudyArguments(BaseModel):
    duration_minutes: int = Field(default=60, ge=15, le=720)
    description: str = Field(default="读书", max_length=100)


class SocialArguments(BaseModel):
    target_id: str
    interaction: str = "conversation"
    description: str = Field(default="交谈", max_length=200)


def _invalid(exc: ValidationError) -> ToolResult:
    return ToolResult(False, f"Invalid arguments: {exc.errors(include_url=False)}")


class SendLetterTool(Tool):
    name = "send_letter"

    def execute(self, context: ToolContext, arguments: dict) -> ToolResult:
        try:
            args = LetterArguments.model_validate(arguments)
            context.world.agents.get(args.target_id)
        except (ValidationError, KeyError) as exc:
            return ToolResult(False, f"Cannot send letter: {exc}")
        event = context.scheduler.schedule(
            EventType.LETTER_CREATED,
            delay=timedelta(minutes=1),
            sender_id=context.actor_id,
            receiver_id=args.target_id,
            payload={"content": args.content},
        )
        return ToolResult(True, "Letter creation scheduled", [event.event_id])


class MoveToTool(Tool):
    name = "move_to"

    def execute(self, context: ToolContext, arguments: dict) -> ToolResult:
        try:
            args = MoveArguments.model_validate(arguments)
            if args.destination_id not in context.world.locations:
                raise KeyError(args.destination_id)
            agent = context.world.agents.get(context.actor_id)
            duration = context.movement.duration(agent.state.location_id, args.destination_id)
        except (ValidationError, KeyError, ValueError) as exc:
            return ToolResult(False, f"Cannot move: {exc}")
        event = context.scheduler.schedule(
            EventType.MOVEMENT_STARTED,
            sender_id=context.actor_id,
            receiver_id=context.actor_id,
            payload={
                "source_id": agent.state.location_id,
                "destination_id": args.destination_id,
                "duration_minutes": int(duration.total_seconds() // 60),
            },
            priority=EventPriority.HIGH,
        )
        return ToolResult(True, "Movement scheduled", [event.event_id])


class StudyTool(Tool):
    name = "study"

    def execute(self, context: ToolContext, arguments: dict) -> ToolResult:
        try:
            args = StudyArguments.model_validate(arguments)
        except ValidationError as exc:
            return _invalid(exc)
        activity = Activity(
            activity_type=ActivityType.STUDY,
            duration_minutes=args.duration_minutes,
            description=args.description,
        )
        event = context.scheduler.schedule(
            EventType.ACTIVITY_START,
            receiver_id=context.actor_id,
            sender_id=context.actor_id,
            payload=activity.model_dump(mode="json"),
        )
        return ToolResult(True, "Study scheduled", [event.event_id])


class SocializeTool(Tool):
    name = "socialize"

    def execute(self, context: ToolContext, arguments: dict) -> ToolResult:
        try:
            args = SocialArguments.model_validate(arguments)
            actor = context.world.agents.get(context.actor_id)
            target = context.world.agents.get(args.target_id)
            if actor.state.location_id != target.state.location_id:
                return ToolResult(False, "Agents are not at the same location")
        except (ValidationError, KeyError) as exc:
            return ToolResult(False, f"Cannot socialize: {exc}")
        event = context.scheduler.schedule(
            EventType.SOCIAL_INTERACTION,
            sender_id=context.actor_id,
            receiver_id=args.target_id,
            payload={"interaction": args.interaction, "description": args.description},
        )
        return ToolResult(True, "Social interaction scheduled", [event.event_id])

