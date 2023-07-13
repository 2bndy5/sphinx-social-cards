import os
from pathlib import Path
from typing import Dict, Optional, cast, List, Union, Any
from urllib.parse import quote

import pydantic
from sphinx.util.logging import getLogger
from .utils import reduce_big_number, strip_url_protocol, get_cache_dir
from ...validators import try_request

LOGGER = getLogger(__name__)

INT_OR_STR = Union[int, str]
OPT_STR = Optional[str]


class BaseUser(pydantic.BaseModel):
    #: The account's name.
    login: str = ""
    #: The account's avatar image's URL.
    avatar: str = ""


class Contributor(BaseUser):
    """|added-ctx| each item listed in the `plugin.vcs.github.repo.contributors
    <Repo.contributors>` :ref:`jinja context <jinja-ctx>`"""

    #: The account's contributions count.
    contributions: INT_OR_STR = 0


class Organization(BaseUser):
    """|added-ctx| each item listed in the `plugin.vcs.github.owner.organizations
    <Owner.organizations>` :ref:`jinja context <jinja-ctx>`"""

    #: The organization's profile description
    description: str = ""


class Repo(pydantic.BaseModel):
    """|added-ctx| `plugin.vcs.github.repo <Github.repo>`
    :ref:`jinja context <jinja-ctx>`"""

    #: The number of repository stars.
    stars: INT_OR_STR = 0
    #: The number of repository watchers.
    watchers: INT_OR_STR = 0
    #: The number of repository forks.
    forks: INT_OR_STR = 0
    #: The name of the license(s).
    license: str = ""
    #: The number of open repository issues.
    open_issues: INT_OR_STR = 0
    #: The `list` of search topics designated for the repository.
    topics: List[str] = []
    #: The name of the repository.
    name: OPT_STR = None
    #: The repository description.
    description: OPT_STR = None
    #: The primarily used program language in the repository.
    language: OPT_STR = None
    languages: Dict[str, float] = {}
    """A `dict` of the used program languages in the repository. Each key is a
    language's name (eg. "Python"), and each value is the corresponding language's
    percent used (eg "97.8").
    """
    #: The repository's designated outreach website |protocol-stripped|
    homepage: OPT_STR = None
    #: The repository GitHub.com URI |protocol-stripped|
    html_url: OPT_STR = None
    tags: List[str] = []
    """A `list`  of the repository's tags (`str`). These values seem to be
    ordered in recent descending to oldest tagged commits."""
    #: A `list`  of the repository's `contributor <Contributor>`\ s.
    contributors: List[Contributor] = []


class Owner(BaseUser):
    """|added-ctx| `plugin.vcs.github.owner <Github.owner>`
    :ref:`jinja context <jinja-ctx>`"""

    #: The account's type (eg "User" or "Organization").
    type: str = ""
    #: The account user's human name.
    name: OPT_STR = None
    #: The number of users that the account is following.
    followers: INT_OR_STR = 0
    #: The number of users that are following the account.
    following: INT_OR_STR = 0
    #: The account profile's brief description.
    bio: OPT_STR = None
    #: A link to a blog site.
    blog: OPT_STR = None
    #: A flag indicating the user is available for employment.
    hirable: Optional[bool] = None
    #: The publicly available email (if any).
    email: OPT_STR = None
    #: The account profile's location.
    location: OPT_STR = None
    #: The number of public repositories for the account.
    public_repos: INT_OR_STR = 0
    #: The number of public gists for the account.
    public_gists: INT_OR_STR = 0
    #: The account user's twitter username.
    twitter_username: OPT_STR = None
    #: The URI to the GitHub.com site |protocol-stripped|
    html_url: OPT_STR = None
    #: A `list`  of the `Organization`\ s to which the account belongs.
    organizations: List[Organization] = []


class Github(pydantic.BaseModel):
    """|added-ctx| ``plugin.vcs.github`` :ref:`jinja context <jinja-ctx>`"""

    #: The github account `owner <Owner>` information.
    owner: Owner = Owner()
    #: The github account `repo <Repo>` information.
    repo: Repo = Repo()


def get_api_token() -> Dict[str, Dict[str, str]]:
    token = os.environ.get("GITHUB_REST_API_TOKEN", "")
    if not token:
        return {}
    return {"headers": {"Authorization": token}}


def get_context_github(owner: Optional[str], repo: Optional[str]) -> Dict[str, Any]:
    gh_ctx = Github()
    if owner is None:
        return gh_ctx.model_dump()
    cache_dir = get_cache_dir()
    owner_cache_name = quote(owner)
    owner_cache_file = Path(cache_dir, owner_cache_name).with_suffix(".json")
    request_args = get_api_token()
    if owner_cache_file.exists():
        gh_ctx.owner = Owner.model_validate_json(
            owner_cache_file.read_text(encoding="utf-8")
        )
    else:
        owner_cache_file.parent.mkdir(parents=True, exist_ok=True)
        # get github account account info
        LOGGER.info("Fetching info for github context about account: %s", owner)
        res_json = try_request(
            f"https://api.github.com/users/{owner}", **request_args
        ).json()
        assert isinstance(res_json, dict)
        gh_ctx.owner = Owner(
            **{
                key: res_json.get(key)
                for key in [
                    "login",
                    "type",
                    "name",
                    "followers",
                    "following",
                    "bio",
                    "blog",
                    "email",
                    "location",
                    "hirable",
                    "public_repos",
                    "public_gists",
                    "twitter_username",
                ]
                if key in res_json
            }
        )
        gh_ctx.owner.avatar = res_json.get("avatar_url", "")
        gh_ctx.owner.html_url = strip_url_protocol(res_json.get("html_url", ""))
        if "organizations_url" in res_json:
            response = try_request(res_json["organizations_url"], **request_args).json()
            for org in cast(List[Dict[str, str]], response):
                gh_ctx.owner.organizations.append(
                    Organization(
                        login=org.get("login", ""),
                        avatar=org.get("avatar_url", ""),
                        description=org.get("description", ""),
                    )
                )
        owner_cache_file.write_text(
            gh_ctx.owner.model_dump_json(indent=2), encoding="utf-8"
        )

    if repo is None:
        return gh_ctx.model_dump()
    # its a repo
    repo_cache_name = quote("/".join([owner, quote(repo)]))
    repo_cache_file = Path(cache_dir, repo_cache_name).with_suffix(".json")
    if repo_cache_file.exists():
        gh_ctx.repo = Repo.model_validate_json(
            repo_cache_file.read_text(encoding="utf-8")
        )
    else:
        repo_cache_file.parent.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Fetching info for github context about repo: %s/%s", owner, repo)
        res_json = try_request(f"https://api.github.com/repos/{owner}/{repo}").json()
        res_json = cast(Dict[str, Any], res_json)
        license_name = ""
        if isinstance(res_json.get("license", None), dict):
            license_name = res_json.get("license", {}).get("name", "")
        gh_ctx.repo = Repo(
            stars=reduce_big_number(res_json.get("stargazers_count", 0)),
            watchers=reduce_big_number(res_json.get("watchers_count", 0)),
            forks=reduce_big_number(res_json.get("forks", 0)),
            license=license_name,
            open_issues=reduce_big_number(res_json.get("open_issues_count", 0)),
            topics=res_json.get("topics", []),
            name=res_json.get("name", ""),
            description=res_json.get("description", ""),
            language=res_json.get("language", ""),
            homepage=strip_url_protocol(res_json.get("homepage", "")),
            html_url=strip_url_protocol(res_json.get("html_url", "")),
        )
        if "languages_url" in res_json:
            langs = try_request(res_json["languages_url"]).json()
            langs = cast(Dict[str, float], langs)
            # convert arbitrary units to percentages
            total = sum(list(langs.values()))
            for lang in langs:
                langs[lang] = round(langs[lang] / total * 100, 1)
            gh_ctx.repo.languages = langs
        if "contributors_url" in res_json:
            response = try_request(res_json["contributors_url"]).json()
            response = cast(List[Dict[str, Any]], response)
            gh_ctx.repo.contributors = [
                Contributor(
                    login=u["login"],
                    avatar=u["avatar_url"],
                    contributions=u["contributions"],
                )
                for u in response
            ]
        if "tags_url" in res_json:
            response = try_request(res_json["tags_url"]).json()
            gh_ctx.repo.tags = [t["name"] for t in cast(List[Dict[str, str]], response)]
        repo_cache_file.write_text(
            gh_ctx.repo.model_dump_json(indent=2), encoding="utf-8"
        )

    return gh_ctx.model_dump()
