from config.constants import EventType
from core.scheduler import Scheduler
from core.world import AudienceType


def schedule_court_summons(scheduler: Scheduler, agent_id: str, case_id: str) -> None:
    scheduler.schedule(
        EventType.ENVIRONMENT,
        payload={
            "audience": AudienceType.DIRECT,
            "audience_value": agent_id,
            "perception_type": "court_summons",
            "description": f"收到案件 {case_id} 的到堂传票。",
            "importance": 90,
        },
    )

