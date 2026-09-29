import unittest

from planning.plan import Plan, Task, TaskStatus


class PlanningTests(unittest.TestCase):
    def test_dependencies_gate_tasks(self) -> None:
        first = Task(task_id="a", description="A", action_name="study", priority=10)
        second = Task(
            task_id="b",
            description="B",
            action_name="move_to",
            dependencies={"a"},
            priority=90,
        )
        plan = Plan(plan_id="p", goal_id="g", tasks=[first, second])
        self.assertEqual([task.task_id for task in plan.ready_tasks()], ["a"])
        first.status = TaskStatus.COMPLETED
        self.assertEqual([task.task_id for task in plan.ready_tasks()], ["b"])


if __name__ == "__main__":
    unittest.main()

