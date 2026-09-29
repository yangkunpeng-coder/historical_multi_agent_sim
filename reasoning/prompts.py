import json

from agents.agent import HistoricalAgent
from agents.perception import Perception


SYSTEM_PROMPT = """你是历史社会模拟中的角色决策器。你只能选择工具，不能直接修改世界。
请只输出一个 JSON 对象，字段为 thought_summary、action_name、action_arguments、finish。
thought_summary 只写简短决策依据，不写详细思维过程。action_name 必须来自可用工具。"""


def build_prompt(agent: HistoricalAgent, perception: Perception, tool_names: list[str]) -> str:
    memories = [item.content for item in agent.memory.recent(5)]
    goals = [goal.description for goal in agent.goals.active()]
    context = {
        "角色": agent.profile.model_dump(mode="json"),
        "状态": agent.state.model_dump(mode="json"),
        "当前观察": perception.model_dump(mode="json"),
        "近期记忆": memories,
        "活跃目标": goals,
        "可用工具": tool_names,
    }
    return SYSTEM_PROMPT + "\n\n情境：\n" + json.dumps(context, ensure_ascii=False)

