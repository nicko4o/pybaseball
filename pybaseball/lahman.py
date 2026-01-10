import logging
from os import path
from typing import Optional
from zipfile import ZipFile

import pandas as pd

from . import cache

logger = logging.getLogger('pybaseball')

# The original GitHub repository (chadwickbureau/baseballdatabank) no longer exists.
# The Lahman Database has been donated to SABR and is now available at:
# https://sabr.org/lahman-database/
#
# Since SABR uses Box.com for hosting (which requires JavaScript/browser download),
# we support loading from locally extracted CSV files.
SABR_DOWNLOAD_URL = "https://sabr.org/lahman-database/"

# Expected directory name after extracting the SABR zip file
# The SABR zip typically extracts to a folder like "lahman_2025" or similar
# We'll search for common patterns
EXPECTED_DIR_PATTERNS = [
    "lahman_*",       # SABR pattern: lahman_2025
    "lahman-*",       # Alternative pattern
    "baseballdatabank*",  # Legacy pattern for backwards compatibility
]

_handle: Optional[ZipFile] = None
_base_dir: Optional[str] = None


def _find_lahman_directory() -> Optional[str]:
    """
    Search for the Lahman database directory in the cache.

    The SABR zip file extracts to different folder names (e.g., "lahman_2025"),
    so we need to search for common patterns.
    """
    import glob

    cache_dir = cache.config.cache_directory

    for pattern in EXPECTED_DIR_PATTERNS:
        matches = glob.glob(path.join(cache_dir, pattern))
        for match in matches:
            # Check if this directory contains the expected structure
            if path.isdir(match):
                core_dir = path.join(match, 'core')
                if path.isdir(core_dir):
                    # Found a valid Lahman directory with core/ subfolder
                    return match
                # Some versions might have CSV files directly in the folder
                people_csv = path.join(match, 'People.csv')
                if path.isfile(people_csv):
                    return match

    return None


def get_lahman_zip() -> Optional[ZipFile]:
    """
    Get the Lahman database ZipFile handle, if available.

    Note: Since the original GitHub source is no longer available,
    this function will raise an error directing users to manually
    download from SABR.
    """
    global _handle, _base_dir

    # First check if we have locally extracted files
    local_dir = _find_lahman_directory()
    if local_dir:
        _base_dir = local_dir
        _handle = None
        return None

    # If no local directory found, raise informative error
    raise RuntimeError(
        f"Lahman database not found in cache directory: {cache.config.cache_directory}\n\n"
        f"The original GitHub source (chadwickbureau/baseballdatabank) is no longer available.\n"
        f"Please manually download the CSV version from SABR:\n\n"
        f"  1. Visit: {SABR_DOWNLOAD_URL}\n"
        f"  2. Download the 'Comma-delimited version' (zip file)\n"
        f"  3. Extract the contents to: {cache.config.cache_directory}\n\n"
        f"After extraction, you should have a folder like 'lahman_2025' containing 'core/' subdirectory."
    )


def download_lahman() -> None:
    """
    Download the Lahman database.

    Note: Automatic download is no longer supported because SABR uses Box.com
    which requires JavaScript/browser interaction. This function now provides
    instructions for manual download.
    """
    raise RuntimeError(
        f"Automatic download is no longer supported.\n\n"
        f"The original GitHub source is no longer available, and SABR's Box.com\n"
        f"hosting requires browser-based download.\n\n"
        f"Please manually download the CSV version from SABR:\n\n"
        f"  1. Visit: {SABR_DOWNLOAD_URL}\n"
        f"  2. Download the 'Comma-delimited version' (zip file)\n"
        f"  3. Extract the contents to: {cache.config.cache_directory}\n\n"
        f"After extraction, you can use the lahman functions normally."
    )


def _get_file(tablename: str, quotechar: str = "'") -> pd.DataFrame:
    """
    Load a CSV file from the Lahman database.

    Args:
        tablename: Path to the CSV file within the Lahman directory (e.g., 'core/People.csv')
        quotechar: Quote character used in the CSV file

    Returns:
        DataFrame containing the CSV data
    """
    global _base_dir

    # Ensure we have a directory to read from
    if _base_dir is None:
        get_lahman_zip()  # This will set _base_dir or raise an error

    if _base_dir is None:
        raise RuntimeError("Lahman database directory not found")

    file_path = path.join(_base_dir, tablename)

    # Handle case where SABR might use different directory structure
    if not path.exists(file_path):
        # Try without subdirectory (some versions have flat structure)
        basename = path.basename(tablename)
        file_path = path.join(_base_dir, basename)

    if not path.exists(file_path):
        raise FileNotFoundError(
            f"Could not find {tablename} in Lahman database at {_base_dir}\n"
            f"Expected path: {path.join(_base_dir, tablename)}"
        )

    return pd.read_csv(
        file_path,
        header=0,
        sep=',',
        quotechar=quotechar
    )


# do this for every table in the lahman db so they can exist as separate functions
def parks() -> pd.DataFrame:
    return _get_file('core/Parks.csv')

def all_star_full() -> pd.DataFrame:
    return _get_file("core/AllstarFull.csv")

def appearances() -> pd.DataFrame:
    return _get_file("core/Appearances.csv")

def awards_managers() -> pd.DataFrame:
    return _get_file("contrib/AwardsManagers.csv")

def awards_players() -> pd.DataFrame:
    return _get_file("contrib/AwardsPlayers.csv")

def awards_share_managers() -> pd.DataFrame:
    return _get_file("contrib/AwardsShareManagers.csv")

def awards_share_players() -> pd.DataFrame:
    return _get_file("contrib/AwardsSharePlayers.csv")

def batting() -> pd.DataFrame:
    return _get_file("core/Batting.csv")

def batting_post() -> pd.DataFrame:
    return _get_file("core/BattingPost.csv")

def college_playing() -> pd.DataFrame:
    return _get_file("contrib/CollegePlaying.csv")

def fielding() -> pd.DataFrame:
    return _get_file("core/Fielding.csv")

def fielding_of() -> pd.DataFrame:
    return _get_file("core/FieldingOF.csv")

def fielding_of_split() -> pd.DataFrame:
    return _get_file("core/FieldingOFsplit.csv")

def fielding_post() -> pd.DataFrame:
    return _get_file("core/FieldingPost.csv")

def hall_of_fame() -> pd.DataFrame:
    return _get_file("contrib/HallOfFame.csv")

def home_games() -> pd.DataFrame:
    return _get_file("core/HomeGames.csv")

def managers() -> pd.DataFrame:
    return _get_file("core/Managers.csv")

def managers_half() -> pd.DataFrame:
    return _get_file("core/ManagersHalf.csv")

def master() -> pd.DataFrame:
    # Alias for people -- the new name for master
    return people()

def people() -> pd.DataFrame:
    return _get_file("core/People.csv")

def pitching() -> pd.DataFrame:
    return _get_file("core/Pitching.csv")

def pitching_post() -> pd.DataFrame:
    return _get_file("core/PitchingPost.csv")

def salaries() -> pd.DataFrame:
    return _get_file("contrib/Salaries.csv")

def schools() -> pd.DataFrame:
    return _get_file("contrib/Schools.csv", quotechar='"')  # different here bc of doublequotes used in some school names

def series_post() -> pd.DataFrame:
    return _get_file("core/SeriesPost.csv")

def teams_core() -> pd.DataFrame:
    return _get_file("core/Teams.csv")

def teams_upstream() -> pd.DataFrame:
    return _get_file("upstream/Teams.csv") # manually maintained file

def teams_franchises() -> pd.DataFrame:
    return _get_file("core/TeamsFranchises.csv")

def teams_half() -> pd.DataFrame:
    return _get_file("core/TeamsHalf.csv")
