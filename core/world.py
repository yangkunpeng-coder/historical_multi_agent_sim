from enum import StrEnum

from agents.registry import AgentRegistry
from spatial.location import Location


class AudienceType(StrEnum):
    GLOBAL = "global"
    ROLE = "role"
    LOCATION = "location"
    DIRECT = "direct"


class World:
    def __init__(self, agents: AgentRegistry | None = None) -> None:
        self.agents = agents or AgentRegistry()
        self.locations: dict[str, Location] = {}

    def add_location(self, location: Location) -> None:
        if location.location_id in self.locations:
            raise ValueError(f"Duplicate location: {location.location_id}")
        self.locations[location.location_id] = location

    def move_agent(self, agent_id: str, destination_id: str) -> None:
        if destination_id not in self.locations:
            raise KeyError(f"Unknown destination: {destination_id}")
        occupancy = len(self.agents.at_location(destination_id))
        if occupancy >= self.locations[destination_id].capacity:
            raise RuntimeError(f"Location is full: {destination_id}")
        self.agents.get(agent_id).state.location_id = destination_id

    def resolve_recipients(
        self,
        audience: AudienceType,
        *,
        value: str | None = None,
        exclude_id: str | None = None,
    ) -> list[str]:
        if audience == AudienceType.GLOBAL:
            agents = self.agents.all()
        elif audience == AudienceType.ROLE and value:
            agents = self.agents.by_role(value)
        elif audience == AudienceType.LOCATION and value:
            agents = self.agents.at_location(value)
        elif audience == AudienceType.DIRECT and value:
            agents = [self.agents.get(value)]
        else:
            raise ValueError("Audience value is required for non-global events")
        return [agent.agent_id for agent in agents if agent.agent_id != exclude_id]

