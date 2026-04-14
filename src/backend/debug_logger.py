from datetime import datetime
from typing import Any


class DebugLogger:
    def log_error(self, error_message: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] ERROR: {error_message}"

    def format_debug_output(self, execution_result: dict[str, Any]) -> tuple[str, str]:
        stdout = execution_result.get("stdout", "")
        stderr = execution_result.get("stderr", "")
        code = execution_result.get("returncode", 1)

        output_block = stdout.strip() or "No stdout output."
        if code == 0:
            error_block = "No errors."
        else:
            base = stderr.strip() or f"Process exited with status {code}."
            error_block = self.log_error(base)

        return output_block, error_block
