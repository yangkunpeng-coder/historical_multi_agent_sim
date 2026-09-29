from datetime import datetime, timedelta

from activity.activity import Activity, ActivityType
from activity.routine import DailyRoutine
from config.constants import EventPriority, EventType
from core.scheduler import Scheduler


class ActivityManager:
    def __init__(self, owner_id: str, routine: DailyRoutine | None = None) -> None:
        self.owner_id = owner_id
        self.routine = routine

    def schedule_activity(
        self,
        scheduler: Scheduler,
        activity: Activity,
        *,
        start_at: datetime | None = None,
    ) -> None:
        scheduler.schedule(
            EventType.ACTIVITY_START,
            trigger_time=start_at,
            receiver_id=self.owner_id,
            payload=activity.model_dump(mode="json"),
            priority=EventPriority.NORMAL,
        )

    def schedule_day(self, scheduler: Scheduler, day: datetime) -> None:
        if self.routine is None:
            return
        for slot in self.routine.ordered():
            start_at = day.replace(
                hour=slot.start.hour,
                minute=slot.start.minute,
                second=0,
                microsecond=0,
            )
            if start_at >= scheduler.now:
                self.schedule_activity(scheduler, slot.activity, start_at=start_at)

    @staticmethod
    def effects(activity_type: ActivityType) -> dict[str, int]:
        return {
            ActivityType.REST: {"energy": 25},
            ActivityType.WORK: {"energy": -15, "money": 2},
            ActivityType.STUDY: {"energy": -10, "knowledge": 4},
            ActivityType.OFFICIAL_DUTY: {"energy": -12},
            ActivityType.SOCIAL: {"energy": -5},
            ActivityType.TRAVEL: {"energy": -10},
            ActivityType.SPECIAL_TASK: {"energy": -15},
        }[activity_type]
