import os
import datetime
import logging
import re
from typing import Optional, NamedTuple, List
import unicodedata

from wiki_data_dump.mirrors import _Mirror


CACHE_LOCATION = os.path.join(os.path.dirname(__file__), "_caches")
CACHE_EXTENSION = ".wiki_dump_cache"  # Identifies cache files in the cache dir. This is unique and verbose for safety.


_reserved_characters = {
    "#", "%", "&", "{",
    "}", "<", ">", "*",
    "?", "/", "$", "!",
    "'", '"', ":", "@",
    "+", "`", "|", "=",
    "\\"
}  # Commonly prohibited or discouraged characters in filenames.


_dunder_match = re.compile(r"__+")
_extension_match = re.compile(rf"{CACHE_EXTENSION}$")


class CacheResult(NamedTuple):
    """Contains the result of a cache request, with the path created/found and the content if file exists."""
    path: str
    content: Optional[str]


def _normalize_name(name: str) -> str:
    """Normalizes non-formatted names to file-system-friendly names.
    Used for caching mirror indices to their own files."""

    def map_chr(ch) -> str:
        if ch in _reserved_characters:
            return ''
        elif ch == ".":
            #  Valid filename character,
            #  but will make extension
            #  checking more difficult.
            return ''
        elif ch == " ":
            return '_'
        return ch

    kd_form = unicodedata.normalize('NFKD', name)
    name = "".join(map_chr(c) for c in kd_form if not unicodedata.combining(c))
    name = _dunder_match.sub("_", name).rstrip("_")
    assert name, "cached file name must normalize to a non-empty string"

    return name.lower()


def _get_today() -> str:
    """Gets date for today in string format [YYYYMMDD]"""
    return datetime.date.today().strftime("%Y%m%d")


def get_cache(mirror: _Mirror, cache_dir: Optional[str]) -> CacheResult:
    """Gets cached mirror index file, and creates one if none exists.
    Cached filenames are in the format './_caches/[mirror_name]__[YYYMMDD of creation].wiki_dump_cache'"""
    today = _get_today()
    filename = f"{_normalize_name(mirror.name)}__{today}{CACHE_EXTENSION}"

    cache_dir = cache_dir if cache_dir else CACHE_LOCATION

    path = os.path.join(cache_dir, filename)

    tail, _ = os.path.split(os.path.abspath(path))
    assert tail == os.path.abspath(cache_dir)
    #  Make sure mirror name does not move filename out of cache dir.

    if os.path.exists(path):
        with open(path, 'r') as f_buffer:
            content = f_buffer.read()
        return CacheResult(path, content if content else None)

    if not os.path.exists(CACHE_LOCATION):
        os.mkdir(CACHE_LOCATION)

    open(path, 'w').close()  # Make file.
    return CacheResult(path, content=None)


def clear_expired_caches(cache_dir: Optional[str]) -> List[str]:
    """Returns a list of names of cache files that were removed because the date created has passed."""

    removed: List[str] = []

    cache_dir = cache_dir if cache_dir else CACHE_LOCATION

    for name in os.listdir(cache_dir):
        without_extension = _extension_match.sub("", name)
        if without_extension != name:
            #  Contains cache extension.
            try:
                _name, _date = without_extension.split("__")
                assert _name and _date
                _ = datetime.datetime.strptime(_date, "%Y%m%d")  # Make sure valid date.
            except (ValueError, AssertionError):
                #  If invalid date or no name/date, do not delete file.
                continue
            if _date != _get_today():
                os.remove(os.path.join(cache_dir, name))
                removed.append(name)
    logging.info(f"Removed files in cache: {removed}")
    return removed


def force_clear_caches(cache_dir: Optional[str] = None) -> List[str]:
    """Returns list of names of removed files in cache."""

    cache_dir = cache_dir if cache_dir else CACHE_LOCATION

    logging.warning("Removing all cache files from cache.")
    removed = []
    for f in os.listdir(cache_dir):
        if f.endswith(CACHE_EXTENSION):
            removed.append(f)
            os.remove(os.path.join(cache_dir, f))
    logging.info(f"Removed files in cache: {removed}")
    return removed
