from config.constants import EventType
from core.scheduler import Scheduler
from core.world import AudienceType


def schedule_tax_notice(scheduler: Scheduler, village_id: str, amount: int) -> None:
    scheduler.schedule(
        EventType.ENVIRONMENT,
        payload={
            "audience": AudienceType.LOCATION,
            "audience_value": village_id,
            "perception_type": "tax_notice",
            "description": f"县衙下达本期征税告示，定额 {amount} 文。",
            "importance": 75,
        },
    )

