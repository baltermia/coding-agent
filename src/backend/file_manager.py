from pathlib import Path


class FileManager:
    def __init__(self, project_root: str) -> None:
        self.project_root = Path(project_root).resolve()
        self.allowed_suffixes = {".py", ".js", ".ts", ".html", ".css", ".json", ".md", ".txt"}

    def list_files(self) -> list[str]:
        files: list[str] = []
        for path in self.project_root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in self.allowed_suffixes:
                continue
            if any(part.startswith(".") for part in path.relative_to(self.project_root).parts):
                continue
            files.append(str(path.relative_to(self.project_root)))
        return sorted(files)

    def _resolve_path(self, relative_path: str) -> Path:
        candidate = (self.project_root / relative_path).resolve()
        if self.project_root not in candidate.parents and candidate != self.project_root:
            raise ValueError("Invalid path outside project root")
        return candidate

    def read_file(self, file_path: str) -> str:
        path = self._resolve_path(file_path)
        return path.read_text(encoding="utf-8")

    def save_file(self, file_path: str, content: str) -> None:
        path = self._resolve_path(file_path)
        path.write_text(content, encoding="utf-8")
