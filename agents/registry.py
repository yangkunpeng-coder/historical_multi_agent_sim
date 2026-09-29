from agents.agent import HistoricalAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, HistoricalAgent] = {}

    def add(self, agent: HistoricalAgent) -> None:
        if agent.agent_id in self._agents:
            raise ValueError(f"Duplicate agent: {agent.agent_id}")
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> HistoricalAgent:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(f"Unknown agent: {agent_id}") from exc

    def all(self) -> list[HistoricalAgent]:
        return list(self._agents.values())

    def by_role(self, role: str) -> list[HistoricalAgent]:
        return [agent for agent in self._agents.values() if agent.profile.role == role]

    def at_location(self, location_id: str) -> list[HistoricalAgent]:
        return [agent for agent in self._agents.values() if agent.state.location_id == location_id]

