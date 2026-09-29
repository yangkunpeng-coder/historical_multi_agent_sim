from enum import StrEnum

from pydantic import BaseModel, Field


class ActivityType(StrEnum):
    REST = "rest"
    WORK = "work"
    STUDY = "study"
    OFFICIAL_DUTY = "official_duty"
    SOCIAL = "social"
    TRAVEL = "travel"
    SPECIAL_TASK = "special_task"


class Activity(BaseModel):
    activity_type: ActivityType
    duration_minutes: int = Field(ge=1)
    description: str = ""

