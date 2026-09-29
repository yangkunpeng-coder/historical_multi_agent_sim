from datetime import timedelta


class MovementService:
    def __init__(self, travel_minutes: dict[tuple[str, str], int]) -> None:
        self._travel_minutes = travel_minutes

    def duration(self, source_id: str, destination_id: str) -> timedelta:
        if source_id == destination_id:
            return timedelta(0)
        minutes = self._travel_minutes.get((source_id, destination_id))
        if minutes is None:
            minutes = self._travel_minutes.get((destination_id, source_id))
        if minutes is None:
            raise ValueError(f"No route from {source_id} to {destination_id}")
        return timedelta(minutes=minutes)

