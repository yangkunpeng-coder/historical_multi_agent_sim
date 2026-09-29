from pydantic import BaseModel, ConfigDict, Field


class Relationship(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    source: str
    target: str
    trust: int = Field(default=0, ge=-100, le=100)
    affinity: int = Field(default=0, ge=-100, le=100)
    familiarity: int = Field(default=0, ge=0, le=100)
    cooperation: int = Field(default=0, ge=0, le=100)
    conflict: int = Field(default=0, ge=0, le=100)

