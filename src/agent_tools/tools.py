import os

MAX_READ_CHARS = 10000


def add_numbers(a: int, b: int) -> int:
    """Adds two numbers together.

    Args:
        a: The first number to add
        b: The second number to add

    Returns:
        The sum of the two numbers
    """
    return a + b


def list_directory(path: str) -> str:
    """Lists visible entries in a directory.

    Hidden entries (starting with ".") are excluded. Directories are suffixed
    with "/" to make them easy to identify.

    Args:
        path: Path to a directory.

    Returns:
        A newline-separated list of entries, or an error/status message.
    """
    abs_path = os.path.abspath(path)

    if not os.path.exists(abs_path):
        return f"Path not found: {abs_path}"
    if not os.path.isdir(abs_path):
        return f"Not a directory: {abs_path}"

    entries = sorted(
        entry for entry in os.listdir(abs_path) if not entry.startswith(".")
    )
    if not entries:
        return f"Directory is empty: {abs_path}"

    formatted_entries = []
    for entry in entries:
        full_entry_path = os.path.join(abs_path, entry)
        suffix = "/" if os.path.isdir(full_entry_path) else ""
        formatted_entries.append(f"{entry}{suffix}")

    return "\n".join(formatted_entries)


def read_file(path: str, max_read_chars: int = MAX_READ_CHARS) -> str:
    """Reads UTF-8 text from a file and truncates overly long output.

    Args:
        path: Path to a file.
        max_read_chars: Maximum number of characters to return.

    Returns:
        Full file contents, truncated contents, or an error/status message.
    """
    abs_path = os.path.abspath(path)

    if not os.path.exists(abs_path):
        return f"Path not found: {abs_path}"
    if not os.path.isfile(abs_path):
        return f"Not a file: {abs_path}"

    with open(abs_path, "r", encoding="utf-8", errors="replace") as file:
        contents = file.read()

    if contents == "":
        return f"File is empty: {abs_path}"

    if len(contents) > max_read_chars:
        return (
            f"{contents[:max_read_chars]}\n\n"
            f"[Output truncated to {max_read_chars} characters]"
        )

    return contents
