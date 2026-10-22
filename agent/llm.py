import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class LLMClient:
    def __init__(self, model: str | None = None):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 中设置 OPENAI_API_KEY")

        base_url = os.getenv("OPENAI_BASE_URL")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url

        self.client = OpenAI(**kwargs)

    def chat(self, messages, tools=None):
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        return self.client.chat.completions.create(**params)