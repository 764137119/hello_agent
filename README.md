```bash
### 方式一：用 crewai CLI（推荐）
### 构建虚拟环境
uv venv 是 Python 包管理工具 uv 提供的命令，用于创建 Python 虚拟环境。
uv venv {{虚拟环境名称}}
uv venv {{虚拟环境名称}} --python 3.12 ##指定python 版本
 ### 启动虚拟环境
source .venv/bin/activate
### 虚拟环境内执行
uv pip install crewai 
### 创建项目
crewai create crew hello-agent



# 先在项目根目录安装依赖
uv sync

# 然后运行
uv run

## 退出虚拟环境

deactivate
```

该项目的环境目录如下 
~/work/golang/crewai-agent
命令 source .venv/bin/activate 在此目录下执行


### crewai 如何做到 像vscode 插件中的 plan. act 模式。 先plan. 人工确认后切到act

这个需求用 CrewAI 的 **Flow + `@human_feedback` + `@router`** 组合就可以实现。我给你设计一个完整的 Plan → Act 模式：

## 架构设计

```
         @start()
            │
            ▼
    ┌─────────────────┐
    │  Plan Crew       │  ← AI 先生成计划
    │  (planner agent) │
    └────────┬────────┘
             │ 输出计划
             ▼
    ┌─────────────────┐
    │  @human_feedback │  ← 展示计划给人类，等待确认
    │   "请审核该计划"  │
    └────────┬────────┘
             │
      ┌──────┴──────┐
      ▼              ▼
  "approved"     "rejected"
      │              │
      ▼              ▼
┌──────────┐  ┌──────────┐
│ Act Crew  │  │ 返回修改  │
│ 执行计划  │  │ 重新规划  │
└──────────┘  └──────────┘
```

## 完整代码示例

### 项目结构
```
src/my_flow/
├── crews/
│   ├── plan_crew/            # Plan Crew
│   │   ├── config/
│   │   │   ├── agents.yaml
│   │   │   └── tasks.yaml
│   │   └── plan_crew.py
│   └── act_crew/             # Act Crew
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       └── act_crew.py
├── main.py                   # Flow 编排
└── flow.py                   # Plan → Act 流程
```

### 1. Plan Crew（生成计划）

**`crews/plan_crew/config/agents.yaml`**：
```yaml
planner:
  role: >
    {topic} Strategy Planner
  goal: >
    Create a detailed step-by-step plan for {topic}
  backstory: >
    You're a strategic planner who breaks down complex topics
    into actionable steps. Known for your clear and structured plans.
```

**`crews/plan_crew/config/tasks.yaml`**：
```yaml
planning_task:
  description: >
    Create a detailed plan for: {topic}
    Break it down into clear, actionable steps.
    Consider timeline, resources needed, and potential risks.
  expected_output: >
    A detailed plan with 5-10 steps, each step including:
    - What needs to be done
    - Expected outcome
    - Dependencies (if any)
    Format as markdown.
  agent: planner
```

### 2. Act Crew（执行计划）

**`crews/act_crew/config/agents.yaml`**：
```yaml
executor:
  role: >
    {topic} Execution Specialist
  goal: >
    Execute the approved plan for {topic} step by step
  backstory: >
    You're a reliable executor who follows plans precisely.
    You complete each step thoroughly before moving to the next.
```

**`crews/act_crew/config/tasks.yaml`**：
```yaml
execution_task:
  description: >
    Execute the following plan step by step:
    
    {plan}
    
    Complete each step thoroughly. Report progress after each step.
  expected_output: >
    A complete execution report with:
    - Each step executed
    - Results achieved
    - Any challenges encountered and how they were resolved
  agent: executor
```

### 3. Flow 编排（核心）

**`flow.py`**：
```python
from crewai.flow.flow import Flow, listen, router, start
from crewai.flow.human_feedback import human_feedback
from pydantic import BaseModel

from my_flow.crews.plan_crew.plan_crew import PlanCrew
from my_flow.crews.act_crew.act_crew import ActCrew

class PlanActState(BaseModel):
    topic: str = ""
    plan: str = ""
    result: str = ""

class PlanActFlow(Flow[PlanActState]):

    @start()
    def generate_plan(self):
        """Step 1: AI 先生成计划"""
        print("\n🤖 AI is generating a plan...\n")
        
        result = PlanCrew().crew().kickoff(
            inputs={"topic": self.state.topic}
        )
        self.state.plan = result.raw
        
        print("\n" + "="*50)
        print("📋 AI 生成的计划:")
        print("="*50)
        print(self.state.plan)
        print("="*50)
        
        return self.state.plan

    @router(generate_plan)
    @human_feedback(
        message="请审核上面的计划，是否同意执行？",
        emit=["approved", "rejected"],
    )
    def review_plan(self, plan: str):
        """Step 2: 等待人工审核"""
        # human_feedback 会暂停，等待用户在终端输入
        # 根据输入内容自动路由到 "approved" 或 "rejected"
        return plan

    @listen("approved")
    def execute_plan(self, plan: str):
        """Step 3: 人工同意后执行"""
        print("\n✅ Plan approved! Executing...\n")
        
        result = ActCrew().crew().kickoff(
            inputs={
                "topic": self.state.topic,
                "plan": self.state.plan,
            }
        )
        self.state.result = result.raw
        
        print("\n" + "="*50)
        print("📊 执行结果:")
        print("="*50)
        print(self.state.result)
        
        return self.state.result

    @listen("rejected")
    def revise_plan(self):
        """Step 4: 被拒绝后重新生成"""
        print("\n❌ Plan rejected. Let me revise...\n")
        
        # 可以在这里获取人类反馈
        feedback = self.last_human_feedback
        print(f"📝 Human feedback: {feedback}")
        
        # 重新规划（回到第一步，或者用反馈优化）
        return self.generate_plan()
```

**`main.py`**：
```python
#!/usr/bin/env python
from my_flow.flow import PlanActFlow

def kickoff():
    flow = PlanActFlow()
    result = flow.kickoff(inputs={"topic": "AI Agent 开发最佳实践"})
    print(f"\n最终结果: {result}")

if __name__ == "__main__":
    kickoff()
```

## 运行效果

```
🤖 AI is generating a plan...

==================================================
📋 AI 生成的计划:
==================================================
Step 1: 研究现有的 AI Agent 框架...
Step 2: 比较不同框架的优缺点...
Step 3: 选择最适合的技术栈...
Step 4: 实现原型系统...
Step 5: 测试和优化...
==================================================

[等待人工输入...]
请审核上面的计划，是否同意执行？ (approved/rejected): _
```

如果你输入 `approved`，则继续执行 Act Crew；
如果你输入 `rejected`，则重新生成计划。

## 和 VS Code Plan/Act 的对比

| VS Code Cline 插件 | CrewAI 实现 |
|-------------------|------------|
| Plan Mode（AI 生成计划） | `@start()` → Plan Crew |
| 人工阅读计划，切换 Act | `@human_feedback` 暂停等待 |
| Act Mode（AI 执行计划） | `@listen("approved")` → Act Crew |
| 返回 Plan 修改 | `@listen("rejected")` → 重新规划 |



实现 Plan → Act 模式最简单的组合是：

| 组件 | 作用 |
|------|------|
| **Flow** | 编排整个流程 |
| **`@human_feedback`** | 暂停等待人工审核 |
| **`@router`** | 根据审核结果走不同分支 |
| **多个 Crew** | 一个负责规划，一个负责执行 |

需要我切换到 ACT MODE 帮你用这个模式改造当前项目，实际跑起来看看效果吗？