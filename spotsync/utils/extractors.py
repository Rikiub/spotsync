import json
from pathlib import Path
from typing import Union


def get_cwd() -> Path:
    """Get 'current working directory', simple."""

    return Path.cwd()


def check_dir(path: Union[Path, str]) -> Path:
    """Check if path/dir exist. Used for argparse"""

    path = Path(path)
    if path.exists():
        return path
    else:
        raise ValueError


def check_playlist_changes(target_file: Path, playlist_name: str) -> bool:
    """Check if the playlist name was changed."""

    if target_file.parent.name != playlist_name:
        return True

    return False


def extract_local_playlist_name(target_file: Path) -> str:
    """Extract playlist name from '.spotdl' file."""

    try:
        with target_file.open("r", encoding="utf8") as file:
            data = json.load(file)
            return data["songs"][0]["list_name"]
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f'"{target_file}" file was not created')  # type: ignore
