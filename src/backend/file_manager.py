from pathlib import Path
from typing import Any


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

    def _is_hidden(self, path: Path) -> bool:
        return any(part.startswith(".") for part in path.relative_to(self.project_root).parts)

    def _build(self, dir_path: Path) -> dict[str, Any]:
        node = {
            "name": dir_path.name,
            "type": "dir",
            "children_dirs": [],
            "children_files": []
        }

        # sort for stable output
        entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name))

        for entry in entries:
            if self._is_hidden(entry):
                continue

            if entry.is_dir():
                node["children_dirs"].append(self._build(entry))
            elif entry.is_file():
                if entry.suffix.lower() not in self.allowed_suffixes:
                    continue
                node["children_files"].append({
                    "name": entry.name,
                    "type": "file",
                })

        return node

    def build_tree(self, root: Path | None = None) -> dict[str, Any]:
        if root is None:
            root = self.project_root

        return self._build(root)


    def _resolve_path(self, relative_path: str) -> Path:
        candidate = (self.project_root / relative_path).resolve()
        if self.project_root not in candidate.parents and candidate != self.project_root:
            raise ValueError("Invalid path outside project root")
        return candidate

    def read_file(self, file_path: str) -> str:
        path = self._resolve_path(file_path)
        return path.read_text(encoding="utf-8")

    def read_file_absolute(self, root_path: str, file_name: str) -> str:
        path = Path(root_path+"/"+file_name)
        return path.read_text(encoding="utf-8")

    def save_file(self, file_path: str, content: str) -> None:
        path = self._resolve_path(file_path)
        path.write_text(content, encoding="utf-8")

    def save_file_in_current_directory(self, file_path: str, content: str) -> None:
        path = Path(file_path)
        path.write_text(content, encoding="utf-8")
