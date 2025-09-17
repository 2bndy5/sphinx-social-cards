from pathlib import Path
from typing import List
import pytest
from sphinx.testing.util import SphinxTestApp


@pytest.mark.parametrize("include", [["index.rst"], []], ids=["include-index", "include-none"])
@pytest.mark.parametrize("exclude", [["index.rst"], []], ids=["exclude-index", "exclude-none"])
@pytest.mark.parametrize("enable", [True, False], ids=["enabled", "disabled"])
def test_transform(
    sphinx_make_app,
    caplog: pytest.LogCaptureFixture,
    include: List[str],
    exclude: List[str],
    enable: bool,
):
    caplog.set_level(10, "sphinx.sphinx_social_cards")
    app: SphinxTestApp = sphinx_make_app(
        extra_conf=f"""
social_cards["cards_include"] = {include}
social_cards["cards_exclude"] = {exclude}
social_cards["enable"] = {enable}
""",
        files={
            "index.rst": """
:title: A test
:description: A unit test of the extension
:icon: sphinx_logo
:card-icon: images/message

Test Title
==========
"""
        },
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())


@pytest.mark.parametrize("dry_run", [True, False], ids=["dry", "wet"])
@pytest.mark.parametrize(
    "with_args,conf_caption",
    ([True, True], [True, False], [False, False]),
    ids=["args+conf_caption", "args+no_conf_caption", "no_args+no_conf_caption"],
)
@pytest.mark.parametrize("meta_caption", [True, False], ids=["meta_caption", "no_meta_caption"])
@pytest.mark.parametrize(
    "layout_caption", [True, False], ids=["layout_caption", "no_layout_caption"]
)
def test_directive(
    sphinx_make_app,
    caplog: pytest.LogCaptureFixture,
    dry_run: bool,
    with_args: bool,
    conf_caption: bool,
    meta_caption: bool,
    layout_caption: bool,
):
    dir_arg = '{ "description": "A unit test of the extension" }'
    caplog.set_level(10, "sphinx.sphinx_social_cards")
    app: SphinxTestApp = sphinx_make_app(
        files={
            "index.rst": f"""

Test Title
==========

.. social-card:: {dir_arg if with_args else ""}
    :meta-data: {{ "title": "A test" }}
    :conf-caption: {"A caption" if not conf_caption else ""}
    :meta-data-caption: {"A caption" if not meta_caption else ""}
    :layout-caption: {"A caption" if not layout_caption else ""}
    {":dry-run:" if dry_run else ""}

    layers: []
"""
        },
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())


@pytest.mark.parametrize("via_directive", [True, False], ids=["directive", "transform"])
def test_builder_check(sphinx_make_app, caplog: pytest.LogCaptureFixture, via_directive: bool):
    caplog.set_level(10, "sphinx.sphinx_social_cards")
    app: SphinxTestApp = sphinx_make_app(
        buildername="latex",
        files={
            "index.rst": f"""
Test Title
==========

.. social-card::
    {":dry-run:" if not via_directive else ""}
"""
        },
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())


def test_flush_cache(sphinx_make_app, caplog: pytest.LogCaptureFixture, tmp_path: Path):
    caplog.set_level(10, "sphinx.sphinx_social_cards")
    app: SphinxTestApp = sphinx_make_app(
        files={
            "index.rst": """
Test Title
==========

.. social-card::
    :dry-run:

    layers:
      - icon: { image: sphinx_logo }
        size: { width: 200, height: 200 }
"""
        },
    )

    app.build()
    assert not app._warning.getvalue()
    test_cache = tmp_path / "social_cards_cache" / ".social_card_examples"
    assert list(test_cache.glob("*.png"))
    # print(list(test_cache.glob("*.png")))
    app._status.flush()
    app.build(True)
    # print(app._status.getvalue())
