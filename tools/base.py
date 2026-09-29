from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from core.scheduler import Scheduler
from core.world import World
from spatial.movement import MovementService


@dataclass(frozen=True)
class ToolContext:
    actor_id: str
    world: World
    scheduler: Scheduler
    movement: MovementService


@dataclass(frozen=True)
class ToolResult:
    success: bool
    message: str
    event_ids: list[str] = field(default_factory=list)


class Tool(ABC):
    name: str

    @abstractmethod
    def execute(self, context: ToolContext, arguments: dict) -> ToolResult:
        raise NotImplementedError

