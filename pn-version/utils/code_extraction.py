from pathlib import Path
import re
import unicodedata
import string
from utils.log import logger


def extract_markers(text: str, marker="!!!") -> list[str]:
    match = re.search(f"{marker}(.*?){marker}", text, flags=re.DOTALL)
    if not match:
        return []

    code = match.group(1)

    code = re.sub(r"```", "", code)
    code = re.sub(r"^\s*python\s*$", "", code, flags=re.MULTILINE)

    lines = code.splitlines()
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    return lines


def normalize_filename(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.replace(" ", "_").lower()
    text = "".join(c for c in text if c in string.ascii_letters + string.digits + "_")
    text = text.strip("_")
    return text or "script"


def save_code(goal: str, response: str, out_dir="scripts") -> Path:
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    filename = normalize_filename(goal) + ".py"
    filepath = Path(out_dir) / filename

    code_lines = extract_markers(response)
    code = "\n".join(code_lines)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    logger.info(f"[GENERATOR] Saved script: {filepath}")
    return filepath
