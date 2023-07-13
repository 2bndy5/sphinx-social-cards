"""
This plugin demonstrates how to add custom context and layouts. The purpose here is
to get information from GitHub (eg stars, forks, etc) and use it in a
new pre-designed layout.

Enabling
********

To enable this plugin, add it to your list of sphinx :confval:`extensions` in conf.py:

.. code-block:: python

    extensions = [
        "sphinx_social_cards",
        "sphinx_social_cards.plugins.github",
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
.. _appdirs: https://github.com/ActiveState/appdirs

To cache the owner/repository information, the appdirs_ dependency is needed. This
can either be install directly:

.. code-block:: shell

    pip install appdirs

or using the ``sphinx-social-cards`` package's optional dependency:

.. code-block:: text
    :caption: requirements.txt

    sphinx-social-cards[github]

.. abstract:: Implementation details about the cached information
    :collapsible:

    By default, the cache of owner/repository information is updated once a day (unless
    the cache is purged).

    .. literalinclude:: ../../src/sphinx_social_cards/plugins/github/utils.py
        :caption: How the cache location is chosen via appdirs_ API
        :language: python
        :pyobject: get_cache_dir

    .. code-annotations::
        1. Following the appdirs_ README, this will create a cache according to the
           OS used:

           - On Windows:
             ``%LOCALAPPDATA%\\2bndy5\\sphinx_social_cards.plugins.github\\Cache\\<month>
             <day> <year>``
           - On Linux:
             ``/home/$(whoami)/.cache/sphinx_social_cards.plugins.github/<month> <day> <year>``
           - On MacOS:
             ``/Users/$(id -un)/Library/Caches/sphinx_social_cards.plugins.github/<month> <day>
             <year>``
"""
from pathlib import Path
from typing import Tuple

from sphinx.application import Sphinx
from sphinx.util.logging import getLogger
from .utils import match_url
from .context import get_context_github
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
    owner, repo = match_url(repo_url, site_url)

    if owner is None and repo is None:
        LOGGER.warning("Failed to identify owner/repository from %s", repo_url)

    # Add the custom layouts to the `cards_layout_dir` list
    add_layouts_dir(app, Path(__file__).parent / "layouts")

    # Use information to get a JSON payload from a REST API call
    gh_ctx = get_context_github(owner, repo)

    # Add the fetched information to the builder environment
    add_jinja_context(app, {"github": gh_ctx})


def setup(app: Sphinx):
    app.connect("builder-inited", on_builder_init)
    app.add_config_value("repo_url", default="", rebuild="html", types=[str])
