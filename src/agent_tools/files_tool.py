import os

from src.agent_core.tools.base import Tool, ToolParameter


class FilesTool(Tool):
    _instance = None
    _max_read_chars = 10000

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            Tool.__init__(
                cls._instance,
                "files",
                "Lists directory entries like ls and reads file contents like cat.",
                [
                    ToolParameter(
                        name="path",
                        description="Path to a directory or file",
                        type="string",
                        required=True,
                    ),
                    ToolParameter(
                        name="action",
                        description='One of: "auto", "list", or "read". Defaults to "auto".',
                        type="string",
                        required=False,
                    ),
                ],
            )
        return cls._instance

    def __init__(self) -> None:
        pass

    def execute(self, path: str, action: str = "auto") -> str:
        abs_path = os.path.abspath(path)
        normalized_action = action.lower().strip()

        if normalized_action not in {"auto", "list", "read"}:
            return 'Invalid action. Use "auto", "list", or "read".'

        if not os.path.exists(abs_path):
            return f"Path not found: {abs_path}"

        if normalized_action == "auto":
            normalized_action = "list" if os.path.isdir(abs_path) else "read"

        if normalized_action == "list":
            if not os.path.isdir(abs_path):
                return f"Not a directory: {abs_path}"
            return self._list_directory(abs_path)

        if not os.path.isfile(abs_path):
            return f"Not a file: {abs_path}"
        return self._read_file(abs_path)

    def _list_directory(self, directory_path: str) -> str:
        entries = sorted(
            entry for entry in os.listdir(directory_path) if not entry.startswith(".")
        )
        if not entries:
            return f"Directory is empty: {directory_path}"

        formatted_entries = []
        for entry in entries:
            full_entry_path = os.path.join(directory_path, entry)
            suffix = "/" if os.path.isdir(full_entry_path) else ""
            formatted_entries.append(f"{entry}{suffix}")

        return "\n".join(formatted_entries)

    def _read_file(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="replace") as file:
            contents = file.read()

        if contents == "":
            return f"File is empty: {file_path}"

        if len(contents) > self._max_read_chars:
            truncated = contents[: self._max_read_chars]
            return (
                f"{truncated}\n\n"
                f"[Output truncated to {self._max_read_chars} characters]"
            )

        return contents
