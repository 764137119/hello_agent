from crewai.flow.flow import Flow, start
from pydantic import BaseModel
from plan_act.plan_agent.plan_crew import PlanCrew
from plan_act.act_agent.act_crew import PlanActCrew


class PlanActState(BaseModel):
    topic: str = ""
    plan: str = ""
    result: str = ""

class PlanActFlow(Flow[PlanActState]):

    @start()
    def plan_and_review(self):
        """
        Step 1: AI 生成计划 → 人工审核 → 如果拒绝则根据反馈重新生成 → 循环直到通过
        Step 2: 审核通过后执行计划
        """
        # 获取用户输入的主题
        topic = input("请输入要规划的主题: ").strip()
        if not topic:
            print("主题不能为空!")
            return
        self.state.topic = topic

        iteration = 0
        final_plan = ""

        while True:
            iteration += 1
            print(f"\n{'='*50}")
            print(f"  Iteration {iteration}: AI is generating a plan...")
            print(f"{'='*50}")

            # 生成计划
            result = PlanCrew().crew().kickoff(
                inputs={"topic": self.state.topic}
            )
            plan = result.raw
            self.state.plan = plan
            final_plan = plan

            print("\n" + "=" * 50)
            print(f"  第 {iteration} 次生成的计划:")
            print("=" * 50)
            print(plan)
            print("=" * 50)

            # 等待人工审核
            user_input = input(
                "\n请审核上面的计划。\n"
                "- 输入 'yes' 或 'y' 同意执行\n"
                "- 输入反馈意见要求修改并重新生成\n"
                "请输入: "
            ).strip()

            if user_input.lower() in ["yes", "y", "approved"]:
                print("\n  Plan approved! Proceeding to execution...\n")
                break
            else:
                print(f"\n  收到反馈: {user_input}")
                print("  根据反馈重新生成计划...\n")
                # 将反馈注入到 topic 中，让 PlanCrew 重新生成时考虑反馈
                self.state.topic += f"\n\n## 第 {iteration} 次反馈意见\n{user_input}"

        # 审核通过后执行计划
        print("=" * 50)
        print("  Executing the plan...")
        print("=" * 50)

        exec_result = PlanActCrew().crew().kickoff(
            inputs={
                "topic": self.state.topic,
                "plan": self.state.plan,
            }
        )
        self.state.result = exec_result.raw

        print("\n" + "=" * 50)
        print("  执行结果:")
        print("=" * 50)
        print(self.state.result)
        print("=" * 50)

        return self.state.result