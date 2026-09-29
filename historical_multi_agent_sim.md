# Event-Driven LLM Multi-Agent Historical Simulation Framework


## 核心原则

### Python负责

-   全局时间
-   Event 调度
-   Agent 状态
-   世界状态
-   规则约束
-   权限检查
-   关系更新
-   计划状态管理

### DeepSeek负责

-   当前情境理解
-   行为选择
-   社会决策
-   复杂推理

LLM不能直接修改世界状态。

流程：

    DeepSeek
     ↓
    JSON
     ↓
    Pydantic Validation
     ↓
    Action
     ↓
    Tool
     ↓
    World Update

------------------------------------------------------------------------

# 一、项目结构

    historical_multi_agent_sim/

    ├── main.py

    ├── config/
    │   ├── settings.py
    │   └── constants.py

    ├── core/
    │   ├── clock.py
    │   ├── event.py
    │   ├── event_queue.py
    │   ├── scheduler.py
    │   ├── simulation_engine.py
    │   └── world.py

    ├── agents/
    │   ├── agent.py
    │   ├── state.py
    │   ├── profile.py
    │   ├── perception.py
    │   ├── memory.py
    │   └── registry.py

    ├── planning/
    │   ├── goal.py
    │   ├── plan.py
    │   ├── planner.py
    │   ├── plan_manager.py
    │   └── trigger_policy.py

    ├── reasoning/
    │   ├── react_engine.py
    │   ├── prompts.py
    │   ├── decision_schema.py
    │   └── deepseek_client.py

    ├── tools/
    │   ├── base.py
    │   ├── registry.py
    │   └── social_tools.py

    ├── social/
    │   ├── relationship.py
    │   ├── relationship_manager.py
    │   └── update_policy.py

    ├── activity/
    │   ├── routine.py
    │   ├── activity.py
    │   ├── activity_manager.py
    │   └── interrupt_policy.py

    ├── spatial/
    │   ├── location.py
    │   └── movement.py

    ├── scenarios/
    │   ├── base.py
    │   ├── county_exam.py
    │   ├── taxation.py
    │   └── court_case.py

    ├── storage/
    │   └── event_store.py

    └── tests/

------------------------------------------------------------------------

# 二、核心事件系统

实现：

## SimulationClock

负责：

-   当前模拟时间
-   时间推进
-   时间查询

------------------------------------------------------------------------

## Event

包含：

-   event_id
-   event_type
-   trigger_time
-   priority
-   sender_id
-   receiver_id
-   payload
-   status

状态：

    PENDING
    EXECUTED
    FAILED
    CANCELLED

------------------------------------------------------------------------

## EventQueue

使用 priority queue。

排序：

    trigger_time
    +
    priority

------------------------------------------------------------------------

## Scheduler

Scheduler 是唯一 Event 创建入口。

禁止：

    event_queue.push()

只能：

    scheduler.schedule()

负责：

-   event id生成
-   时间计算
-   priority设置
-   插入EventQueue

------------------------------------------------------------------------

## SimulationEngine

核心：

    while running:

        event = queue.pop()

        clock.advance_to(
            event.trigger_time
        )

        execute(event)

------------------------------------------------------------------------

# 三、Agent系统

Agent：

    HistoricalAgent

    ├── Profile
    ├── State
    ├── Memory
    ├── GoalManager
    ├── PlanManager
    ├── RelationshipManager
    ├── ActivityManager
    └── ReActEngine

------------------------------------------------------------------------

# 四、规划系统

层级：

    Long Term Goal

    ↓

    Long Term Plan

    ↓

    Short Term Goal

    ↓

    Short Term Plan

    ↓

    Task

    ↓

    Action

Task 支持：

-   dependencies
-   priority
-   status
-   completed
-   failed

------------------------------------------------------------------------

# 五、自研ReAct

不要使用 AgentScope。

流程：

    Observation

    ↓

    Context Builder

    ↓

    DeepSeek

    ↓

    Pydantic Decision

    ↓

    Action

    ↓

    Tool

Decision Schema：

    thought_summary

    action_name

    action_arguments

    finish

------------------------------------------------------------------------

# 六、Tool系统

Action 不直接改变世界。

例如：

    send_letter

经过：

    Tool

    ↓

    LETTER_CREATED_EVENT

    ↓

    Scheduler

    ↓

    EventQueue

------------------------------------------------------------------------

# 七、日常活动系统

目标：

模拟 Agent 默认生活状态。

不要模拟：

-   洗脸
-   吃饭细节
-   微观动作

采用：

    REST

    WORK

    STUDY

    OFFICIAL_DUTY

    SOCIAL

    TRAVEL

    SPECIAL_TASK

流程：

    DailyRoutine

    ↓

    ActivityPlanner

    ↓

    Scheduler

    ↓

    ACTIVITY_START

    ↓

    ACTIVITY_FINISH

------------------------------------------------------------------------

# 八、空间系统

采用离散位置。

不使用 GPS。

Location：

    HOME

    FIELD

    MARKET

    COUNTY_OFFICE

    COURT

    EXAM_HALL

    VILLAGE

支持：

-   移动
-   到达事件
-   位置查询

------------------------------------------------------------------------

# 九、社会关系系统

Relationship：

    source

    target

    trust

    affinity

    familiarity

    cooperation

    conflict

关系更新：

    Social Event

    ↓

    RelationshipUpdatePolicy

    ↓

    RelationshipManager

DeepSeek不能直接修改关系。

------------------------------------------------------------------------

# 十、事件传播

支持：

    Environment Event

    ↓

    Recipient Resolver

    ↓

    Perception Event

类型：

-   global event
-   role event
-   location event
-   direct event

------------------------------------------------------------------------
