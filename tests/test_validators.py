from pathlib import Path
from typing import List, Dict, Union, Optional
import pytest
from sphinx.testing.util import SphinxTestApp
from sphinx_social_cards.validators import (
    try_request,
    assert_path_exists,
    _validate_color,
)

PALETTE = {"primary": "green", "accent": "light-green"}


@pytest.mark.xfail
def test_bad_url():
    try_request("")  # should throw an error


@pytest.mark.xfail
def test_bad_path() -> None:
    assert_path_exists(Path("non-existent"))


@pytest.mark.parametrize("color", ["invalid", None])
def test_bad_color(color: Optional[str]):
    assert _validate_color(color) == (color, False)


@pytest.mark.parametrize("palette", [PALETTE, [PALETTE, PALETTE]], ids=["dict", "list"])
def test_default_immaterial_colors(
    sphinx_make_app, palette: Union[List[Dict[str, str]], Dict[str, str]]
):
    app: SphinxTestApp = sphinx_make_app(
        extra_conf=f"""html_theme = 'sphinx_immaterial'
extensions.append("sphinx_immaterial")
html_theme_options = {{
    "palette": {palette},
}}
social_cards["cards_layout_options"] = {{"background_color ": "#00F"}}
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())


def test_default_colors(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="""html_theme = 'furo'
social_cards["cards_layout_options"] = { "background_color ": "#00F" }
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())


@pytest.mark.parametrize("font", [{"text": "Roboto"}, False], ids=["default", "system"])
def test_default_font(sphinx_make_app, font: Union[Dict[str, str], bool]):
    app: SphinxTestApp = sphinx_make_app(
        extra_conf=f"""html_theme = 'sphinx_immaterial'
extensions.append("sphinx_immaterial")
html_theme_options = {{
    "font": {font},
}}
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())


@pytest.mark.parametrize(
    "logo,svg",
    (
        [None, "material/library"],
        [
            "https://github.com/jbms/sphinx-immaterial/raw/"
            + "e9f3c94fbd6b23dd78d699c47102cb2d3f4a0008/docs/_static/images/Ybin.gif",
            "material/library",
        ],
        pytest.param(None, "non-existent", marks=pytest.mark.xfail),
        pytest.param("https://bad-url", "", marks=pytest.mark.xfail),
    ),
    ids=["bundled", "url", "invalid_svg", "bad_url"],
)
def test_default_logo(sphinx_make_app, logo: Optional[str], svg: str):
    app: SphinxTestApp = sphinx_make_app(
        extra_conf=f"""html_theme = 'sphinx_immaterial'
extensions.append("sphinx_immaterial")
html_theme_options = {{
    "icon": {{ "logo": "{svg}" }},
}}
html_logo = {repr(logo)}
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())


@pytest.mark.xfail
def test_custom_img_path(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="""html_theme = 'furo'
social_cards["image_paths"] = ["non-existent"]
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())


def test_debugging_helpers(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="""html_theme = 'furo'
social_cards["debug"] = True
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())
