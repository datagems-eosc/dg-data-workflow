from pathlib import Path


def build_file_path(directory: str, name: str, extension: str | None = None) -> Path:
    """
    Construct a full file path from directory, name, and extension components.
    If no extension is provided, the file will have none.

    Args:
        directory (str): The directory path.
        name (str): The file name (without extension).
        extension (str | None): The file extension (with or without leading dot). Optional.

    Returns:
        Path: The combined pathlib.Path object.
    """
    if extension:
        ext = extension if extension.startswith(".") else f".{extension}"
        filename = f"{name}{ext}"
    else:
        filename = name

    return Path(directory) / filename
