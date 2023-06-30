from pathlib import Path
import platform
import re
import shutil
import time
from typing import Tuple, Optional, Union, List, Dict, Any
from urllib.parse import urlparse

from appdirs import user_cache_dir
from sphinx.util.logging import getLogger
from ....validators import try_request

LOGGER = getLogger(__name__)


def get_response(url: str) -> Tuple[Union[List[Dict[str, Any]], Dict[str, Any]], int]:
    response = try_request(url)
    if response.status_code == 200:
        return response.json(), response.status_code
    LOGGER.error("Got %d response from URL %r", response.status_code, url)
    return {}, response.status_code


def reduce_big_number(numb: int) -> str:
    if numb < 1000:
        return str(numb)
    elif numb >= 1000000:
        return f"{round(numb / 1000000, 2)}M"
    return f"{round(numb / 1000, 2)}k"


def strip_url_protocol(url: str) -> str:
    if not url:
        return url
    url_parts = urlparse(url)
    return f"{url_parts.netloc}{url_parts.path}"


def match_url(
    repo_url: str, site_url: str
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    LOGGER.info("repo_url: %s", repo_url)
    match_repo_url = re.match(
        r"^.+github\.com\/([^/]+)\/?([^/]+)?",
        repo_url,
    )
    match_gh_pages_url = re.match(r"^[^:]+://(.*).github.io/(.*)/?$", site_url)
    owner, repo, service = (None, None, None)
    if match_repo_url is not None:
        owner, repo = match_repo_url.groups()[:2]
        service = "github"
    elif match_gh_pages_url is not None:
        owner, repo = match_gh_pages_url.groups()[:2]
        service = "github"
    return owner, repo, service


def get_cache_dir() -> str:
    time_fmt = "%B %#d %Y" if platform.system().lower() == "windows" else "%B %-d %Y"
    today = time.strftime(time_fmt, time.localtime())
    cache_dir = Path(
        user_cache_dir("sphinx_social_cards.plugins.vcs", "2bndy5", version=today)
    )
    if cache_dir.parent.exists() and not cache_dir.exists():
        # purge the old cache
        shutil.rmtree(cache_dir.parent)
    return str(cache_dir)
