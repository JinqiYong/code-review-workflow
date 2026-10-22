import json

from .llm import LLMClient
from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from .tools import TOOL_SCHEMAS, execute_tool


class CodeReviewAgent:
    def __init__(self, llm: LLMClient, max_steps: int = 8):
        self.llm = llm
        self.max_steps = max_steps

    def run(self, target: str) -> str:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(target=target)},
        ]

        for _ in range(self.max_steps):
            response = self.llm.chat(messages, tools=TOOL_SCHEMAS)
            msg = response.choices[0].message

            assistant_msg = {"role": "assistant", "content": msg.content or ""}
            if msg.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]

            messages.append(assistant_msg)

            if not msg.tool_calls:
                return msg.content or "模型未返回内容。"

            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}

                result = execute_tool(name, args)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    }
                )

        return "达到最大工具调用步数，未能生成最终报告。请缩小审查范围或增加 max_steps。"