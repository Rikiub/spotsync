from pathlib import Path
from typing import Union

from requests.exceptions import ConnectionError
from spotdl import Downloader
from spotdl.console.entry_point import generate_initial_config, sync
from spotdl.utils.config import (
    DEFAULT_CONFIG,
    SPOTIFY_OPTIONS,
    get_cache_path,
    get_config,
)
from spotdl.utils.logging import init_logging
from spotdl.utils.spotify import SpotifyClient
from spotipy import CacheFileHandler, Spotify, SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials

from spotsync.utils.theme import print

VALID_URLS = "https://open.spotify.com/playlist/"


def getSpotifyClient() -> Spotify:
    """A Spotipy instance using the SpotDL cache path."""

    config = user_config()

    auth_manager = SpotifyClientCredentials(
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        cache_handler=CacheFileHandler(cache_path=get_cache_path()),
    )
    return Spotify(auth_manager=auth_manager)


def check_spotify_url(url: str) -> str:
    """Check URL with Spotipy."""

    try:
        sp = getSpotifyClient()
        if sp.playlist(url):
            return url

        raise ConnectionError()
    except SpotifyException:
        print(url, "[warning]is not a valid Spotify URL.")
        raise ValueError
    except ConnectionError:
        print("[warning]Failed to connect to internet.")
        raise


def user_config() -> dict:
    """
    Return SpotDL user config file.
    In Linux and Darwin the path is '~/.spotdl/config.json'
    """

    generate_initial_config()
    return get_config()


instance = None


def spotDLSyncer(
    query: Union[Path, str], output_path: Path, save_file: str | None = None
) -> None:
    """
    A little "hack" to uses SpotDL on Python scripts without errors.
    Adapted to just uses "sync" command.

    ## Arguments
    query:
      "str(URL)" to Spotify playlist. That run the creation of an new Playlist folder.
      "pathlib.Path" to .spotdl file. That run the sync of an current Playlist folder.
    output_path:
      where the files will be stored.
    save_file:
      name of the '.spotdl' file.
    """

    # persistent instance options
    global instance
    downloader = None

    try:
        # if instance not exist, init a "singleton" instance
        if not instance:
            # init SpotDL Singleton
            SpotifyClient.init(**SPOTIFY_OPTIONS)
            init_logging("INFO")
            instance = True

        # set spotsync defaults
        default_settings = DEFAULT_CONFIG
        default_settings["audio_providers"] = [
            "soundcloud",
            "bandcamp",
            "youtube-music",
        ]
        default_settings["lyrics_providers"] = [
            "synced",
            "musixmatch",
            "genius",
            "azlyrics",
        ]
        default_settings["preload"] = True
        default_settings["bitrate"] = "auto"

        default_settings["output"] = str(output_path)

        # if "query" is a path run playlist creation mode. You need specify a "save_file" name or error got.
        if isinstance(query, str):
            if save_file:
                default_settings["save_file"] = str(f"{output_path}/{save_file}")
            else:
                raise ValueError(
                    "For playlist creation mode you need provide a 'save_file' name."
                )
        # elif "query" is a Path, run playlist sync mode.
        elif isinstance(query, Path):
            query = str(query)

        # read user config from '~/.spotdl/config.json' (Linux and Darwin example)
        custom_settings = user_config()
        default_settings["format"] = custom_settings["format"]
        default_settings["detect_formats"] = custom_settings["detect_formats"]

        # parse custom settings
        downloader = Downloader(default_settings)

        # Init Functions
        query_aux = [query]
        sync(query_aux, downloader)

    except (ConnectionError, SpotifyException):
        print("[warning]Failed to connect to internet.")
    except ValueError:
        import traceback

        traceback.print_exc()
        raise
    except KeyboardInterrupt:
        raise
    finally:
        if downloader:
            downloader.progress_handler.close()
