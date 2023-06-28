from pathlib import Path
import pytest
from sphinx.testing.util import SphinxTestApp

TEST_LAYOUT = str(Path(__file__).parent / "layouts").replace("\\", "\\\\")


@pytest.mark.parametrize(
    "name,layout",
    (
        ["default", ""],
        pytest.param("custom", "", marks=pytest.mark.xfail),
        ["", "layers: []"],
        pytest.param("invalid", "", marks=pytest.mark.xfail),
    ),
    ids=["default", "non-existent", "valid", "invalid"],
)
def test_parse_layout(sphinx_make_app, name: str, layout: str):
    app: SphinxTestApp = sphinx_make_app(
        extra_conf=f"""html_theme = 'furo'
social_cards["debug"] = {{
    "enable": True,
    "color": "#0FF1CE",
}}
social_cards["cards_layout_dir"] = ['{TEST_LAYOUT}']
""",
        files={
            "index.rst": f"""
Test Title
==========

.. image-generator:: {name}

    {layout}
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()


@pytest.mark.parametrize("radius", [315, 600])
def test_rectangle(sphinx_make_app, radius: int):
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="html_theme = 'furo'",
        files={
            "index.rst": f"""
Test Title
==========

.. image-generator::

    layers:
      - rectangle:
          color: '#FFFFFF7F'
          radius: {radius}
          border:
            width: 25
            color: white
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()


def test_ellipse(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="html_theme = 'furo'",
        files={
            "index.rst": """
Test Title
==========

.. image-generator::

    layers:
      - ellipse:
          color: '#FFFFFF7F'
          border:
            width: 25
            color: white
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()


def test_typography(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="html_theme = 'furo'",
        files={
            "index.rst": """
Test Title
==========

.. image-generator::

    layers:
      - typography:
          content: |
            S
             S
              C

          overflow: on
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()
