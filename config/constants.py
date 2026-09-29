from enum import IntEnum, StrEnum


class EventPriority(IntEnum):
    CRITICAL = 0
    HIGH = 25
    NORMAL = 50
    LOW = 75


class EventType(StrEnum):
    ENVIRONMENT = "environment"
    PERCEPTION = "perception"
    AGENT_DECISION = "agent_decision"
    LETTER_CREATED = "letter_created"
    LETTER_DELIVERED = "letter_delivered"
    ACTIVITY_START = "activity_start"
    ACTIVITY_FINISH = "activity_finish"
    MOVEMENT_STARTED = "movement_started"
    ARRIVAL = "arrival"
    SOCIAL_INTERACTION = "social_interaction"


DEFAULT_EVENT_LIMIT = 1_000
DEFAULT_TRAVEL_MINUTES = 60
DEFAULT_ACTIVITY_MINUTES = 60

