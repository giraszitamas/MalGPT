import os
from pathlib import Path
import time
from typing import Dict
from dotenv import load_dotenv
import openai
from core.prompts import DISC_BASE_PROMPT


load_dotenv()


class Disc:
    def __init__(self, model="gpt-4.1-mini", temperature=0.2, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
        self.model = model
        self.temperature = temperature

    def evaluate(self, attack_sample: str) -> str:
        prompt = DISC_BASE_PROMPT + f"Evaluate the following attack sample:\n{attack_sample}"
        response = openai.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature
        )
        return response.choices[0].message.content.strip()

    def evaluate_scripts(
            self,
            scripts_dir: str = "scripts",
            *,
            key_type: str = "name",
            recursive: bool = False,
            pattern: str = "*.py",
            retries: int = 2,
            backoff_base: float = 0.5,
    ) -> Dict[str, str]:
        results: dict[str, str] = {}
        base = Path(scripts_dir)

        if recursive:
            file_iter = sorted(base.rglob(pattern))
        else:
            file_iter = sorted(base.glob(pattern))

        for path in file_iter:
            if key_type == "name":
                key = path.name
            elif key_type == "relpath":
                key = path.relative_to(Path.cwd()).as_posix() if path.is_relative_to(Path.cwd()) else path.as_posix()
            elif key_type == "abspath":
                key = str(path.resolve())
            else:
                raise ValueError("key_type must be one of 'name','relpath','abspath'")

            try:
                content = path.read_text(encoding="utf-8")
            except Exception as e:
                results[key] = f"ERROR: failed to read file: {e}"
                continue

            attempt = 0
            feedback = ""
            while attempt <= retries:
                try:
                    feedback = self.evaluate(content)
                    break
                except Exception as e:
                    attempt += 1
                    if attempt > retries:
                        feedback = f"ERROR: evaluation failed after {retries} retries: {e}"
                        break
                    sleep_for = backoff_base * (2 ** (attempt - 1))
                    time.sleep(sleep_for)

            results[key] = feedback

        return results
