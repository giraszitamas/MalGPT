import ast
from typing import Tuple


def syntax_check(code: str) -> Tuple[bool, str]:
    try:
        ast.parse(code)
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    return True, ""
