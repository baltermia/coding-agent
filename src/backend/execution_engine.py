import ast
import subprocess
import sys
from typing import Any


class ExecutionEngine:
    def run_code(self, code: str) -> dict[str, Any]:
        try:
            ast.parse(code)
        except SyntaxError as err:
            return {
                "ok": False,
                "stdout": "",
                "stderr": f"SyntaxError: {err.msg} (line {err.lineno})",
                "returncode": 1,
            }

        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                check=False,
                capture_output=True,
                text=True,
                timeout=12,
            )
            return {
                "ok": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "stdout": "",
                "stderr": "Execution timed out after 12 seconds.",
                "returncode": 124,
            }
