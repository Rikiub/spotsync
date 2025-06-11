from pathlib import Path
from typing import List, Literal, get_args

from spotsync.utils.extractors import (
    check_playlist_changes,
    extract_local_playlist_name,
)
from spotsync.utils.spotdl import ConnectionError, spotDLSyncer
from spotsync.utils.theme import input, print

SYNC_OPTS = Literal["all", "select"]


def Sync(operation: SYNC_OPTS, output_path: Path, target_file: str):
    """
    Sync current Playlists.
    """

    # check if argument "operation" is a list and convert
    if isinstance(operation, list):
        operation = "all"

    try:
        # "all" operation
        if operation == "all":
            directories = search_dirs(output_path, target_file)

            counter = len(directories)
            for path_object in directories:
                print(f"\n[low]-> [enumerate]{counter}[/]")
                execute_file(path_object)
                counter -= 1

        # "select" operation
        elif operation == "select":
            directories = search_dirs(output_path, target_file)
            selected_dir = select_directory_TUI(directories)

            print("\n[low]-> Selected")
            execute_file(selected_dir)

        # no "operation"? error got
        else:
            raise ValueError(
                "[error]Invalid operation because is expected:", get_args(SYNC_OPTS)
            )

        print("\n[success]Sync successful")

    except (ValueError, FileNotFoundError, KeyboardInterrupt, ConnectionError):
        pass


def search_dirs(output_path: Path, target_file: str) -> List[Path]:
    """
    Search around a directory to found 'target_file'(s).

    ## Arguments
    output_path: directory to search
    target_file: files to found
    """

    # main
    directories = [path for path in output_path.glob("**/" + target_file)]

    # no directories? error got
    if not directories:
        print(f'[warning]No directories found with [object]"{target_file}"[/] file')
        raise FileNotFoundError

    return directories


def execute_file(target_file: Path):
    """Start sync of the founded directories"""

    print(f"[high]Syncing playlist:[/] [item]{target_file.parent.name}[/]")

    # execute spotdl and check if executed successful
    if spotDLSyncer(query=target_file, output_path=target_file.parent):
        # rename directory if remote playlist was change
        playlist_name = extract_local_playlist_name(target_file)

        if check_playlist_changes(target_file, playlist_name):
            print(
                "[spotdl_log]Detected changes in remote Playlist. Renaming directory..."
            )
            target_file.parent.rename(playlist_name)


def select_directory_TUI(directories: List[Path]) -> Path:
    """Simple TUI to select the directory to sync instead of sync all the folders."""

    print()
    for index, directory in enumerate(directories, start=1):
        print(f"[enumerate]{index}.[/] [item]{directory.parent.name}[/]")

    try:
        choice = int(
            input(
                "\n[low]Choose a directory to sync[/] [enumerate][1-"
                + str(len(directories))
                + "][/]: "
            )
        )

        if 1 <= choice <= len(directories):
            dirs = directories[choice - 1]
            return dirs
        else:
            raise ValueError
    except ValueError:
        print("[warning]Please enter a valid index number")
        raise
