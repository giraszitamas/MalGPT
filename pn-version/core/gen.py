import os
from openai import OpenAI
from core.prompts import ATTACK_GOAL_PROMPT
from utils.code_extraction import extract_markers


class Gen:
    def __init__(self, api_key=None, model="gpt-4.1-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def ask(self, prompt: str):
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content

    def get_attack_list(self) -> list[str]:
        content = self.ask(ATTACK_GOAL_PROMPT)
        return extract_markers(content, marker="!!!")
