from agents.state import AgentState


class PlanningTriggerPolicy:
    def should_replan(self, state: AgentState, *, has_ready_task: bool) -> bool:
        return state.available and not has_ready_task

