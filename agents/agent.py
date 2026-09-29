from activity.activity_manager import ActivityManager
from agents.memory import Memory
from agents.profile import AgentProfile
from agents.state import AgentState
from planning.goal import GoalManager
from planning.plan_manager import PlanManager
from social.relationship_manager import RelationshipManager


class HistoricalAgent:
    def __init__(
        self,
        profile: AgentProfile,
        state: AgentState,
        *,
        memory: Memory | None = None,
    ) -> None:
        self.profile = profile
        self.state = state
        self.memory = memory or Memory()
        self.goals = GoalManager()
        self.plans = PlanManager()
        self.relationships = RelationshipManager(profile.agent_id)
        self.activities = ActivityManager(profile.agent_id)
        self.react_engine = None

    @property
    def agent_id(self) -> str:
        return self.profile.agent_id

