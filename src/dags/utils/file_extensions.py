from pathlib import Path


def build_file_path(directory: str, name: str, extension: str | None = None) -> Path:
    if extension:
        ext = extension if extension.startswith(".") else f".{extension}"
        filename = f"{name}{ext}"
    else:
        filename = name

    return Path(directory) / filename
