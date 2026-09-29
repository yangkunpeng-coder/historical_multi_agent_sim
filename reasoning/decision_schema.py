from pydantic import BaseModel, Field


class Decision(BaseModel):
    thought_summary: str = Field(max_length=500)
    action_name: str | None = None
    action_arguments: dict = Field(default_factory=dict)
    finish: bool = False

