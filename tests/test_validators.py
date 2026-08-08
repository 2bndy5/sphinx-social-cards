from pathlib import Path

from importlib.metadata import version as get_version
import pytest
from sphinx.testing.util import SphinxTestApp
from sphinx_social_cards.validators import try_request
from sphinx_social_cards.validators.contexts import Config, today_default


need_sphinx_immaterial_and_pydantic_v2 = pytest.mark.skipif(
    tuple([int(x) for x in get_version("sphinx-immaterial").split(".")[:3]]) < (0, 11, 5),
    reason="pydantic v2 API not used by sphinx-immaterial until v0.11.5",
)

PALETTE = {"primary": "green", "accent": "light-green"}


@pytest.mark.xfail
def test_bad_url():
    try_request("")  # should throw an error


@pytest.mark.parametrize(
    "code,expected",
    (["en", "English"], ["es", "Spanish"], ["xx", "xx"], [None, "English"]),
    ids=["English", "Spanish", "unknown", "None"],
)
def test_ctx_lang_code(code: str | None, expected: str | None):
    assert Config(site_url="", language=code).language == expected


@pytest.mark.parametrize("val", ["today", None], ids=["str", "None"])
def test_ctx_today(val: str | None):
    assert Config(site_url="", today=val).today == val or today_default


@need_sphinx_immaterial_and_pydantic_v2
@pytest.mark.parametrize("palette", [PALETTE, [PALETTE, PALETTE]], ids=["dict", "list"])
def test_default_immaterial_colors(sphinx_make_app, palette: list[dict[str, str]] | dict[str, str]):
    app: SphinxTestApp = sphinx_make_app(
        extra_conf=f"""html_theme = 'sphinx_immaterial'
extensions.append("sphinx_immaterial")
html_theme_options = {{
    "palette": {palette},
}}
social_cards["cards_layout_options"] = {{"background_color": "#00F"}}
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    assert not app._warning.getvalue()  # type: ignore[attr-defined]
    # print(app._status.getvalue())


@need_sphinx_immaterial_and_pydantic_v2
def test_default_colors(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="""
social_cards["cards_layout_options"] = { "background_color ": "#00F" }
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    assert not app._warning.getvalue()  # type: ignore[attr-defined]
    # print(app._status.getvalue())


@need_sphinx_immaterial_and_pydantic_v2
@pytest.mark.parametrize("font", [{"text": "Roboto"}, False], ids=["default", "system"])
def test_default_font(sphinx_make_app, font: dict[str, str] | bool):
    app: SphinxTestApp = sphinx_make_app(
        extra_conf=f"""html_theme = 'sphinx_immaterial'
extensions.append("sphinx_immaterial")
html_theme_options = {{
    "font": {font},
}}
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    assert not app._warning.getvalue()  # type: ignore[attr-defined]
    # print(app._status.getvalue())


@need_sphinx_immaterial_and_pydantic_v2
@pytest.mark.parametrize(
    "logo,svg",
    (
        [None, "material/library"],
        [
            "https://github.com/jbms/sphinx-immaterial/raw/"
            + "e9f3c94fbd6b23dd78d699c47102cb2d3f4a0008/docs/_static/images/Ybin.gif",
            "material/library",
        ],
        [None, "non-existent"],
        pytest.param("https://bad-url", "", marks=pytest.mark.xfail),
    ),
    ids=["bundled", "url", "invalid_svg", "bad_url"],
)
def test_default_logo(sphinx_make_app, logo: str | None, svg: str):
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

    assert not app._warning.getvalue()  # type: ignore[attr-defined]
    # print(app._status.getvalue())


@pytest.mark.xfail
def test_custom_img_path(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="""
social_cards["image_paths"] = ["non-existent"]
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    app.build()
    assert not app._warning.getvalue()  # type: ignore[attr-defined]
    # print(app._status.getvalue())


def test_debugging_helpers(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="""
social_cards["debug"] = True
""",
        files={"index.rst": "\nTest Title\n=========="},
    )

    app.build()
    assert not app._warning.getvalue()  # type: ignore[attr-defined]
    # print(app._status.getvalue())


@pytest.mark.xfail
def test_bad_path(sphinx_make_app):
    # Path must be absolute for this test to fail expectedly
    invalid = Path(__file__).parent / "invalid"
    assert invalid.is_absolute()
    sphinx_make_app(
        extra_conf=f"""
social_cards["cards_layout_dir"] = [{repr(str(invalid))}]
""",
        files={"index.rst": "\nTest Title\n==========\n\n.. image-generator::"},
    )
