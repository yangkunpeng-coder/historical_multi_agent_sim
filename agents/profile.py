from pydantic import BaseModel, Field


class AgentProfile(BaseModel):
    agent_id: str
    name: str
    age: int = Field(ge=0, le=120)
    role: str
    background: str = ""
    traits: list[str] = Field(default_factory=list)

