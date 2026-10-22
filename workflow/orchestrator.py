from workflow.state import WorkflowState
from workflow.agents import CoderAgent, ReviewerAgent, FixerAgent
from agent.llm import LLMClient

class WorkflowOrchestrator:
    def __init__(self):
        llm = LLMClient()
        self.agents = {
            "coder": CoderAgent(llm),
            "reviewer": ReviewerAgent(llm),
            "fixer": FixerAgent(llm),
        }

    def run(self, task: str):
        state = WorkflowState(task=task)
        print(f"开始 Workflow: {task}\n")

        state.current_iteration=1
        state = self.agents["coder"].run(state)
        print(f"[初版代码]:\n{state.current_code}\n")

        # 2 & 3. 循环：审查 -> 修复
        while state.current_iteration < state.max_iterations and not state.is_passed:
            print(f"正在执行第 {state.current_iteration + 1} 轮审查...")
            state = self.agents["reviewer"].run(state)
            print(f"[审查报告]:\n{state.review_history[-1]['report']}\n")

            if state.is_passed:
                print("代码审查通过，流程结束！")
                break
            
            print("审查未通过，进入修复阶段...")
            state = self.agents["fixer"].run(state)
            print(f"[修复后代码]:\n{state.current_code}\n")

            state.current_iteration+=1
        if not state.is_passed:
            print("达到最大迭代次数，流程终止。")

        print("\n=== 执行日志 ===")
        for log in state.logs:
            print(log)
        return state