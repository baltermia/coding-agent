from .system_prompter import SystemPrompter
from .server_utils import get_client, chat


class ChatManager:
    def __init__(self, system_prompter: SystemPrompter) -> None:
        self.system_prompter = system_prompter
        self.client = get_client()

    def send_message(self, message: str, file_context: str = "", debug_context: str = "") -> str:
        prompt = self.system_prompter.generate_prompt(message, file_context, debug_context)

        # Format messages for OpenAI API
        messages = [
            {
                "role": "system",
                "content": self.system_prompter.default_system_prompt,
            },
            {"role": "user", "content": prompt},
        ]

        try:
            # Call the LLM via server_utils
            response = chat(self.client, messages)
            return response
        except Exception as e:
            # Fallback if LLM call fails
            print(f"LLM call failed: {e}")
            return self._fallback_response(message, file_context, debug_context)

    def _fallback_response(self, message: str, file_context: str, debug_context: str) -> str:
        summary = []
        summary.append("I can help with this task. Here is a practical next step:")

        lowered = message.lower()
        if "error" in lowered or "traceback" in lowered:
            summary.append("- Start by reproducing the error with the current file content.")
            if debug_context:
                summary.append("- Use the stderr output to identify the failing line and exception type.")
        elif "optimi" in lowered:
            summary.append("- Identify repeated logic and extract it into helper functions.")
            summary.append("- Add small, focused docstrings and type hints for maintainability.")
        else:
            summary.append("- Describe the exact goal and expected behavior in one sentence.")
            summary.append("- Then apply changes in small increments and run execution after each step.")

        if file_context:
            summary.append("- Context was included from the currently open file.")
        if debug_context:
            summary.append("- Recent execution output was included for debugging context.")

        return "\n".join(summary)
