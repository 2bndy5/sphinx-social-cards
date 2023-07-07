import os
from pathlib import Path
import platform
import sys
import pytest
from sphinx import version_info as sphinx_version
from sphinx.testing.util import SphinxTestApp
from sphinx.errors import ExtensionError
from sphinx_social_cards.plugins import add_images_dir
from sphinx_social_cards.plugins.github.utils import (
    reduce_big_number,
    strip_url_protocol,
)


def test_blank_url():
    assert strip_url_protocol("") == ""


def test_big_number():
    assert reduce_big_number(1048576) == "1M"


@pytest.mark.parametrize(
    "url_key,url",
    (
        ["repo_url", "https://github.com/2bndy5/CirquePinnacle"],
        ["social_cards['site_url']", "https://nRF24.github.io/RF24"],
        pytest.param(
            "social_cards['site_url']", "https://RF24.rtfd.io", marks=pytest.mark.xfail
        ),
        ["repo_url", "https://github.com/2bndy5"],
        ["repo_url", "https://github.com/2bndy5/CirquePinnacle"],
    ),
    ids=["repo_url", "site_url", "invalid_url", "only_owner", "from_cache"],
)
def test_plugin_github(sphinx_make_app, url_key: str, url: str):
    if os.environ.get("CI", False) and (
        platform.system().lower() != "linux"
        or sys.version_info < (3, 11)
        or sphinx_version < (7,)
    ):
        pytest.skip(
            "To avoid REST API rate limit, this test runs (in CI) only on Linux with "
            "Python v3.11+ and Sphinx v7+"
        )
    try:
        app: SphinxTestApp = sphinx_make_app(
            extra_conf=f"""html_theme = "furo"
extensions.append("sphinx_social_cards.plugins.github")
social_cards["cards_layout"] = "github/default"
{url_key}="{url}"
""",
            files={
                "index.rst": """

Test Title
==========
"""
            },
        )

        app.build()
        assert not app._warning.getvalue()
    except (RuntimeError, ExtensionError) as exc:
        if "returned 403" in str(exc):
            pytest.skip(
                "GitHub REST API hit rate limit. Code coverage may be compromised."
            )
        else:
            raise exc


def test_add_images(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="""html_theme="furo"
social_cards["enable"] = False
""",
        files={
            "index.rst": """

Test Title
==========
"""
        },
    )
    add_images_dir(
        app, Path(__file__).parent.parent / "src" / "sphinx_social_cards" / ".icons"
    )
    app.build()
    assert not app._warning.getvalue()
