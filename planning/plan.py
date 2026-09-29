from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    task_id: str
    description: str
    action_name: str
    action_arguments: dict = Field(default_factory=dict)
    dependencies: set[str] = Field(default_factory=set)
    priority: int = Field(default=50, ge=0, le=100)
    status: TaskStatus = TaskStatus.PENDING


class Plan(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    plan_id: str
    goal_id: str
    tasks: list[Task]
    long_term: bool = True

    def ready_tasks(self) -> list[Task]:
        completed = {task.task_id for task in self.tasks if task.status == TaskStatus.COMPLETED}
        return sorted(
            (
                task
                for task in self.tasks
                if task.status == TaskStatus.PENDING and task.dependencies <= completed
            ),
            key=lambda task: task.priority,
            reverse=True,
        )

    @property
    def completed(self) -> bool:
        return bool(self.tasks) and all(task.status == TaskStatus.COMPLETED for task in self.tasks)

