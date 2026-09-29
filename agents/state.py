from pydantic import BaseModel, Field


class AgentState(BaseModel):
    location_id: str
    health: int = Field(default=100, ge=0, le=100)
    energy: int = Field(default=100, ge=0, le=100)
    money: int = Field(default=0, ge=0)
    knowledge: int = Field(default=0, ge=0, le=100)
    current_activity: str | None = None
    available: bool = True

