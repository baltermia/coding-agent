class SystemPrompter:
    def __init__(self) -> None:
        self.default_system_prompt = (
            "You are a code assistant helping to debug and improve Python code. "
            "Prefer practical, safe, and concise suggestions."
        )

    def generate_prompt(self, user_message: str, file_context: str = "", debug_context: str = "") -> str:
        safe_file_context = file_context[:4000]
        safe_debug_context = debug_context[:2000]
        return (
            "<system>\n"
            f"{self.default_system_prompt}\n"
            "</system>\n"
            "<task>\n"
            f"{user_message}\n"
            "</task>\n"
            "<code>\n"
            f"{safe_file_context}\n"
            "</code>\n"
            "<debug>\n"
            f"{safe_debug_context}\n"
            "</debug>"
        )
