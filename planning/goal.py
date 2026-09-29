from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class GoalStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class Goal(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    goal_id: str
    description: str
    priority: int = Field(default=50, ge=0, le=100)
    long_term: bool = True
    status: GoalStatus = GoalStatus.ACTIVE


class GoalManager:
    def __init__(self) -> None:
        self._goals: dict[str, Goal] = {}

    def add(self, goal: Goal) -> None:
        if goal.goal_id in self._goals:
            raise ValueError(f"Duplicate goal: {goal.goal_id}")
        self._goals[goal.goal_id] = goal

    def active(self) -> list[Goal]:
        return sorted(
            (goal for goal in self._goals.values() if goal.status == GoalStatus.ACTIVE),
            key=lambda goal: goal.priority,
            reverse=True,
        )

