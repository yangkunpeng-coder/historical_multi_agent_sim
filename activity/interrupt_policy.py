from activity.activity import ActivityType


class InterruptPolicy:
    _INTERRUPTIBLE = {
        ActivityType.REST,
        ActivityType.WORK,
        ActivityType.STUDY,
        ActivityType.SOCIAL,
    }

    def can_interrupt(self, current: ActivityType | None, *, emergency: bool = False) -> bool:
        return emergency or current is None or current in self._INTERRUPTIBLE

