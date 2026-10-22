import re
import os
from agent.llm import LLMClient
from agent.tools import run_ruff, run_syntax_check

def extract_code(text: str) -> str:
    """剥离 LLM 输出中的 Markdown 代码块标记"""
    match = re.search(r'```(?:python)?\n(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

class CoderAgent:
    def __init__(self, llm: LLMClient): self.llm = llm
    
    def run(self, state):
        prompt = f"请根据任务编写Python代码，只返回代码，不要markdown包裹：\n{state.task}"
        raw_code = self.llm.chat([{"role": "user", "content": prompt}]).choices[0].message.content
        state.current_code = extract_code(raw_code)
        state.add_log("CoderAgent: 初版代码生成完毕")
        return state

class ReviewerAgent:
    def __init__(self, llm: LLMClient): self.llm = llm
    
    def run(self, state):
        temp_file = "temp_review_code.py"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(state.current_code)
        
        ruff_result = run_ruff(temp_file)
        syntax_result = run_syntax_check(temp_file)
        
        if os.path.exists(temp_file): 
            os.remove(temp_file)

        prompt = f"""请审查以下代码。
静态检查结果：{syntax_result} | {ruff_result}
代码内容：
{state.current_code}

请输出审查报告，并务必在最后一行给出明确判定：如果通过写 PASS，不通过写 FAIL。
"""
        response = self.llm.chat([{"role": "user", "content": prompt}]).choices[0].message.content
        state.review_history.append({"iteration": state.current_iteration, "report": response})
        
        if "PASS" in response.upper().split()[-1]:
            state.is_passed = True
            state.add_log("ReviewerAgent: 审查通过")
        else:
            state.is_passed = False
            state.add_log("ReviewerAgent: 审查未通过，打回修复")
        return state

class FixerAgent:
    def __init__(self, llm: LLMClient): self.llm = llm
    
    def run(self, state):
        last_report = state.review_history[-1]["report"]
        prompt = f"请根据审查意见修复代码。\n原代码：\n{state.current_code}\n审查意见：\n{last_report}\n只返回修复后的代码。"
        raw_code = self.llm.chat([{"role": "user", "content": prompt}]).choices[0].message.content
        state.current_code = extract_code(raw_code)
        state.add_log("FixerAgent: 代码修复完毕")
        return state