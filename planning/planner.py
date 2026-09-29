from uuid import uuid4

from planning.goal import Goal
from planning.plan import Plan, Task


class Planner:
    """Rule-based baseline planner; an LLM planner can replace this adapter."""

    def create_plan(self, goal: Goal, task_specs: list[dict]) -> Plan:
        tasks = [Task(**spec) for spec in task_specs]
        return Plan(plan_id=str(uuid4()), goal_id=goal.goal_id, tasks=tasks, long_term=goal.long_term)

