from .context_extractor import ContextExtractor

class SystemPrompter:
    def __init__(self) -> None:
        self.default_system_prompt = (
            "You are a code assistant helping to debug and improve Python code. "
            "Prefer practical, safe, and concise suggestions."
        )
        self.context_extractor = ContextExtractor()

    def generate_prompt(self, user_message: str, file_context: str = "", debug_context: str = "") -> str:
        safe_file_context = file_context[:4000]
        safe_file_context = self.context_extractor.extract_content(safe_file_context, 1, 500) #How do I grab current row?????

        safe_debug_context = debug_context[:2000]
        user_prompt = []

        user_prompt.append("<task>\n"
                        f"{user_message}\n"
                        "</task>\n")
        if safe_file_context:
            user_prompt.append("<code>\n"
                               f"{safe_file_context}\n"
                               "</code>\n")
        if safe_debug_context:
            user_prompt.append("<debug>\n"
                               f"{safe_debug_context}\n"
                               "</debug>")
        
        return "\n".join(user_prompt)