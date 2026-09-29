# 历史多智能体事件模拟框架

这是一个可运行的 Python MVP，实现了事件驱动调度、历史 Agent、分层规划、记忆、社会关系、粗粒度日常活动、离散空间、自研 ReAct 工具调用边界，以及可选的 DeepSeek 决策接口。

设计约束是：LLM 只产生经过 Pydantic 校验的 `Decision`；任何动作必须经由 Tool 转换为 Event；只有 Python 事件处理器可以更新世界、Agent 和关系状态。

## 快速开始

项目需要 Python 3.11+。

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
python main.py --offline
python -m unittest discover -s tests -v
```

离线演示描述晚清江南县的一名士子获知县试日期、温习经义并前往考院的过程。运行后会打印状态摘要，并把所有已执行/失败/取消的事件写入 `simulation_events.jsonl`。

## 使用 DeepSeek

设置环境变量后直接运行；若调用失败或返回 JSON 不合法，系统会记录警告并自动退回确定性策略。

```powershell
$env:DEEPSEEK_API_KEY = "你的密钥"
python main.py
```

可选变量：`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`、`EVENT_STORE_PATH`、`LOG_LEVEL`。
默认模型为 `deepseek-v4-flash`，决策请求关闭 thinking 并要求 JSON Object 输出；模型名可通过 `DEEPSEEK_MODEL` 覆盖。

## 核心数据流

```text
Environment Event -> Perception Event -> ReAct Decision
                                      -> Pydantic validation
                                      -> Tool permission/argument checks
                                      -> new Event -> Python world update
```

`Scheduler.schedule()` 是创建事件的唯一公开入口。`EventQueue` 不暴露公共 `push()`；排序键依次为触发时间、优先级和稳定序号。

## 扩展方式

- 新动作：实现 `tools.base.Tool`，只调度事件，不直接修改状态。
- 新事件：在 `SimulationEngine` 注册对应处理器。
- 新场景：实现 `scenarios.base.Scenario`，负责组装依赖和初始事件。
- 新 LLM：保持 `complete(prompt) -> str` 适配接口，并继续使用 `Decision` 校验。
- 新关系规则：扩展 `RelationshipUpdatePolicy`，不要让 LLM 直接写关系数值。

当前县试场景是演示性模型，不应被理解为精确历史重建。要用于研究，应继续补充史料来源、人口与经济参数、随机种子、批量实验及结果校准。
