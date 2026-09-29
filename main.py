import argparse
import json
import logging
from pathlib import Path

from config.settings import Settings
from scenarios.county_exam import CountyExamScenario
from storage.event_store import JsonlEventStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="历史多智能体事件模拟")
    parser.add_argument("--max-events", type=int, default=100, help="本次最多处理的事件数")
    parser.add_argument(
        "--event-log",
        type=Path,
        default=Path("simulation_events.jsonl"),
        help="JSONL 事件日志路径",
    )
    parser.add_argument("--offline", action="store_true", help="强制使用离线确定性决策器")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = Settings.from_env()
    settings.event_store_path = args.event_log
    if args.offline:
        settings.deepseek_api_key = None
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    runtime = CountyExamScenario(
        settings=settings,
        event_store=JsonlEventStore(settings.event_store_path),
    ).build()
    processed = runtime.engine.run(max_events=args.max_events)
    scholar = runtime.world.agents.get("li_ming")
    summary = {
        "processed_events": processed,
        "simulation_time": runtime.engine.clock.now.isoformat(),
        "agent": scholar.profile.name,
        "location": runtime.world.locations[scholar.state.location_id].name,
        "state": scholar.state.model_dump(mode="json"),
        "memories": [item.content for item in reversed(scholar.memory.recent(5))],
        "plans_completed": [plan.completed for plan in scholar.plans.all()],
        "event_log": str(settings.event_store_path.resolve()),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
