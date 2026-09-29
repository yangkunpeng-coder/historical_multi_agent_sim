import json
import logging
from collections.abc import Callable

from pydantic import ValidationError

from agents.agent import HistoricalAgent
from agents.perception import Perception
from reasoning.decision_schema import Decision
from reasoning.deepseek_client import DeepSeekClient, DeepSeekError
from reasoning.prompts import build_prompt
from tools.base import ToolContext, ToolResult
from tools.registry import ToolRegistry

FallbackPolicy = Callable[[HistoricalAgent, Perception, list[str]], Decision]


class ReActEngine:
    def __init__(
        self,
        client: DeepSeekClient,
        tools: ToolRegistry,
        fallback_policy: FallbackPolicy,
    ) -> None:
        self.client = client
        self.tools = tools
        self.fallback_policy = fallback_policy
        self.logger = logging.getLogger(__name__)

    def decide(self, agent: HistoricalAgent, perception: Perception) -> Decision:
        names = self.tools.names()
        if not self.client.configured:
            return self.fallback_policy(agent, perception, names)
        prompt = build_prompt(agent, perception, names)
        try:
            raw = self.client.complete(prompt)
            return Decision.model_validate(json.loads(raw))
        except (DeepSeekError, ValidationError, json.JSONDecodeError) as exc:
            self.logger.warning("LLM decision invalid; using fallback: %s", exc)
            return self.fallback_policy(agent, perception, names)

    def act(
        self,
        agent: HistoricalAgent,
        perception: Perception,
        context: ToolContext,
    ) -> tuple[Decision, ToolResult | None]:
        decision = self.decide(agent, perception)
        if decision.finish or decision.action_name is None:
            return decision, None
        tool = self.tools.get(decision.action_name)
        return decision, tool.execute(context, decision.action_arguments)


def historical_fallback_policy(
    agent: HistoricalAgent, perception: Perception, tool_names: list[str]
) -> Decision:
    """Deterministic offline policy for the county-exam demo."""
    kind = perception.event_type
    if kind == "exam_announced" and "study" in tool_names:
        return Decision(
            thought_summary="县试将近，应先按计划温习经义。",
            action_name="study",
            action_arguments={"duration_minutes": 180, "description": "温习经义"},
        )
    if kind == "study_completed" and agent.state.knowledge >= 8 and "move_to" in tool_names:
        return Decision(
            thought_summary="准备已有进展，启程前往考院。",
            action_name="move_to",
            action_arguments={"destination_id": "exam_hall"},
        )
    return Decision(thought_summary="眼下无需额外行动。", finish=True)

