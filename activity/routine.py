from datetime import time

from pydantic import BaseModel

from activity.activity import Activity


class RoutineSlot(BaseModel):
    start: time
    activity: Activity


class DailyRoutine(BaseModel):
    slots: list[RoutineSlot]

    def ordered(self) -> list[RoutineSlot]:
        return sorted(self.slots, key=lambda slot: slot.start)

