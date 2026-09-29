from planning.plan import Plan, Task, TaskStatus


class PlanManager:
    def __init__(self) -> None:
        self._plans: dict[str, Plan] = {}

    def add(self, plan: Plan) -> None:
        if plan.plan_id in self._plans:
            raise ValueError(f"Duplicate plan: {plan.plan_id}")
        self._plans[plan.plan_id] = plan

    def next_task(self) -> Task | None:
        ready = [task for plan in self._plans.values() for task in plan.ready_tasks()]
        return max(ready, key=lambda task: task.priority, default=None)

    def mark(self, task_id: str, status: TaskStatus) -> None:
        for plan in self._plans.values():
            for task in plan.tasks:
                if task.task_id == task_id:
                    task.status = status
                    return
        raise KeyError(task_id)

    def all(self) -> list[Plan]:
        return list(self._plans.values())

