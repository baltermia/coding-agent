class ContextExtractor:
    def extract_content(self, file_content: str, cursor_line:int, window: int = 50) -> str:
        lines = file_content.splitlines()

        start = max(0, cursor_line - window)
        end = min(len(lines), cursor_line + window)

        snippet = lines[start:end]

        numbered = []

        for i, line in enumerate(snippet):
            numbered.append(f"{i}: {line}")

        return "\n".join(numbered)