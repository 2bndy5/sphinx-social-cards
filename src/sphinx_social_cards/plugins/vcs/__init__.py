"""
This plugin demonstrates how to add custom context and layouts. The purpose here is
to get VCS (Version Control System) information (eg stars, forks, etc) and use it in a
new pre-designed layout.

This plugin currently only supports GitHub via REST API endpoint(s).

Enabling
********

To enable this plugin, add it to your list of sphinx :confval:`extensions` in conf.py:

.. code-block:: python

    extensions = [
        "sphinx_social_cards",
        "sphinx_social_cards.plugins.vcs",
    ]

Configuration
*************

This extension uses :confval:`html_theme_options`\ [:themeconf:`repo_url`] from
sphinx-immaterial_ configuration value or its own :confval:`repo_url` configuration
value to set the repository URL.

.. confval:: repo_url

    .. code-block:: python
        :caption: conf.py

        repo_url = "https://github.com/2bndy5/sphinx-social-cards"

    The repository's required identifying information (``owner`` and ``repo``) can
    also be parsed from the `site_url <Social_Cards.site_url>` if it uses a standard
    GitHub Pages address (:html:`https://<owner>.github.io/<repo>`).

.. tip::
    Information from GitHub is fetched using GitHub's REST API endpoints. If there is a
    need to authenticate HTTP GET requests from the REST API, then set an environment
    variable ``GITHUB_REST_API_TOKEN`` with the generated access token. This is mostly
    useful when fetching information about private repositories or to avoid the REST API
    rate limit.

Dependencies
************

To cache the owner/repository information, the ``appdirs`` dependency is needed. This
can either be install directly:

.. code-block:: shell

    pip install appdirs

or using the ``sphinx-social-cards`` package's optional dependency:

.. code-block:: text
    :caption: requirements.txt

    sphinx-social-cards[vcs]

.. abstract:: Implementation details about the cached information
    :collapsible:

    By default, the cache of owner/repository information is updated once a day (unless
    the cache is purged).

    .. literalinclude:: ../../src/sphinx_social_cards/plugins/vcs/utils/__init__.py
        :caption: How the cache location is chosen via ``appdirs`` API
        :language: python
        :pyobject: get_cache_dir
"""
from pathlib import Path
from typing import Dict, Any, Tuple

from sphinx.application import Sphinx
from sphinx.util.logging import getLogger
from .utils import match_url
from .utils.github import get_context_github
from .. import (
    SPHINX_SOCIAL_CARDS_CONFIG_KEY,
    add_jinja_context,
    add_layouts_dir,
)
from ...validators import Social_Cards

LOGGER = getLogger(__name__)


def _get_config_info(app: Sphinx) -> Tuple[str, str]:
    # Parse the necessary information from the validated config object
    card_config: Social_Cards = getattr(app.config, SPHINX_SOCIAL_CARDS_CONFIG_KEY)
    # again for sphinx-immaterial theme
    theme_repo_url = getattr(app.config, "html_theme_options", {}).get("repo_url", "")
    # and once more as a hard override from our own extension config key `repo_url`
    ext_repo_url = getattr(app.config, "repo_url", "")  # config value added in setup()
    return ext_repo_url or theme_repo_url, card_config.site_url


def on_builder_init(app: Sphinx):
    repo_url, site_url = _get_config_info(app)
    owner, repo, service = match_url(repo_url, site_url)

    vcs_env: Dict[str, Any] = {}
    if service is None:
        LOGGER.warning("Failed to identify owner/repository from %s", repo_url)

    # Add the custom layouts to the `cards_layout_dir` list
    add_layouts_dir(app, Path(__file__).parent / "layouts")

    # Use information to get a JSON payload from a REST API call
    if service == "github":
        assert owner is not None
        vcs_env["github"] = get_context_github(owner, repo)

    # Add the fetched information to the builder environment
    add_jinja_context(app, {"vcs": vcs_env})


def setup(app: Sphinx):
    app.connect("builder-inited", on_builder_init)
    app.add_config_value("repo_url", default="", rebuild="html", types=[str])
