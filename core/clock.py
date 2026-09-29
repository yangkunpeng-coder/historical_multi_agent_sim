from datetime import datetime, timedelta


class SimulationClock:
    def __init__(self, start_time: datetime) -> None:
        if start_time.tzinfo is None:
            raise ValueError("Simulation time must be timezone-aware")
        self._now = start_time

    @property
    def now(self) -> datetime:
        return self._now

    def advance_to(self, target: datetime) -> None:
        if target.tzinfo is None:
            raise ValueError("Target time must be timezone-aware")
        if target < self._now:
            raise ValueError("Simulation clock cannot move backwards")
        self._now = target

    def after(self, delta: timedelta) -> datetime:
        if delta < timedelta(0):
            raise ValueError("Delta cannot be negative")
        return self._now + delta

