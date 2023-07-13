from pathlib import Path
import platform
import re
import shutil
import time
from typing import Tuple, Optional
from urllib.parse import urlparse

from appdirs import user_cache_dir
from sphinx.util.logging import getLogger

LOGGER = getLogger(__name__)


def reduce_big_number(numb: int) -> str:
    if numb < 1000:
        return str(numb)
    elif numb >= 1000000:
        return f"{int(numb / 1000000)}M"
    return f"{int(numb / 1000)}k"


def strip_url_protocol(url: str) -> str:
    if not url:
        return url
    url_parts = urlparse(url)
    return f"{url_parts.netloc}{url_parts.path}"


def match_url(repo_url: str, site_url: str) -> Tuple[Optional[str], Optional[str]]:
    match_repo_url = re.match(
        r"^.+github\.com\/([^/]+)\/?([^/]+)?",
        repo_url,
    )
    match_gh_pages_url = re.match(r"^[^:]+://(.*).github.io/(.*)/?$", site_url)
    owner, repo = (None, None)
    if match_repo_url is not None:
        owner, repo = match_repo_url.groups()[:2]
    elif match_gh_pages_url is not None:
        owner, repo = match_gh_pages_url.groups()[:2]
    return owner, repo


def get_cache_dir() -> str:
    time_fmt = "%B %#d %Y" if platform.system().lower() == "windows" else "%B %-d %Y"
    today = time.strftime(time_fmt, time.localtime())
    cache_dir = Path(
        user_cache_dir(
            "sphinx_social_cards.plugins.github", "2bndy5", version=today  # (1)!
        )
    )
    if cache_dir.parent.exists() and not cache_dir.exists():
        shutil.rmtree(cache_dir.parent)  # purge the old cache
    return str(cache_dir)
