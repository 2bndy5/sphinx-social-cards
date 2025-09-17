from pathlib import Path
from typing import Union, List
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
        extra_conf=f"""
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


@pytest.mark.parametrize("radius", [0, 315, 600])
@pytest.mark.parametrize(
    "corners",
    (
        ["top left", "top right", "bottom left", "bottom right"],
        ["top right", "bottom left"],
    ),
    ids=["all", "2"],
)
def test_rectangle(sphinx_make_app, radius: int, corners: List[str]):
    app: SphinxTestApp = sphinx_make_app(
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
          corners: [{", ".join(corners)}]
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()


def test_ellipse(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        files={
            "index.rst": """
Test Title
==========

.. image-generator::

    layers:
      - background:
          linear_gradient:
            preset: MorpheusDen # 22
            start: { y: 315 }
            end: { x: 1200, y: 315 }
      - ellipse:
          radial_gradient:
            preset: 85 # OctoberSilence
            center: { x: 600, y: 315 }
            radius: 730
            spread: reflect
            focal_point: { x: 650, y: 200 }
            focal_radius: 2
          border:
            width: 25
            conical_gradient:
              preset: NightParty
              center: { x: 600, y: 315 }
              angle: 387
              colors: { 0.5: yellow }
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()


@pytest.mark.parametrize("overflow", ["on", "off"], ids=["on", "off"])
def test_typography_overflow(sphinx_make_app, overflow: str) -> None:
    app: SphinxTestApp = sphinx_make_app(
        files={
            "index.rst": f"""
Test Title
==========

.. social-card:: {{ "debug": true }}

    size: {{ width: 900, height: 330 }}
    layers:
      - typography:
          content: |-
            Glyphs
                Typography
            Symbols
            PictogramsTypographyGlyphs
          overflow: {overflow}
          line: {{ amount: 3 }}
          align: center
          border:
            color: {"red" if overflow == "on" else "null"}
            width: 1
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()


@pytest.mark.parametrize(
    "content",
    [
        """|
            line 1

            supercalifragilisticexpialidocious""",
        "A really long sentence that occupies multiple lines",
    ],
    ids=["blank_line+long_word", "long_sentence"],
)
def test_typography_content(sphinx_make_app, content: str) -> None:
    app: SphinxTestApp = sphinx_make_app(
        files={
            "index.rst": f"""
Test Title
==========

.. social-card:: {{ "debug": true }}

    size: {{ width: 900, height: 330 }}
    layers:
      - typography:
          content: {content}
          line: {{ amount: 3 }}
          align: center
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()


TEST_AREA = "{ width: 100, height: 100 }"


@pytest.mark.parametrize(
    "size,offset",
    (
        [TEST_AREA, "{}"],
        [TEST_AREA, "{ x: -50, y: -50 }"],
        [TEST_AREA, "{ x: 50, y: 50 }"],
        ["{ width: 200, height: 200 }", "{}"],
    ),
    ids=["same", "pre", "post", "over_sized"],
)
def test_mask(sphinx_make_app, size: str, offset: str):
    inverted = size == TEST_AREA and offset == "{}"  # enable for "same" test case
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="social_cards['enable']=False",
        files={
            "index.rst": f"""
Test Title
==========

.. image-generator::

    size: {TEST_AREA}
    layers:
      - background:
          color: '#fff'
        mask:
          invert: {str(inverted).lower()}
          size: {size}
          offset: {offset}
          ellipse:
            color: '#000'
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()


@pytest.mark.parametrize("layer_attr", ["icon", "background"])
@pytest.mark.parametrize(
    "image,color",
    (
        ["images/rainbow.png", "#0000007F"],
        pytest.param("bad_image", "#0000007F", marks=pytest.mark.xfail),
        pytest.param("images/rainbow.png", "#bad_color", marks=pytest.mark.xfail),
    ),
    ids=["valid_vals", "bad_image", "bad_color"],
)
def test_image(sphinx_make_app, layer_attr: str, image: str, color: str) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="social_cards['enable']=False",
        files={
            "index.rst": f"""
Test Title
==========

.. image-generator::

    layers:
      - {layer_attr}:
          image: '{image}'
          color: '{color}'
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()


@pytest.mark.parametrize("border_to_origin", ["on", "off"])
def test_ellipse_arc(sphinx_make_app, border_to_origin: str) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="social_cards['enable']=False",
        files={
            "index.rst": f"""
Test Title
==========

.. social-card:: {{ "debug": true }}

    size: {{ width: 900, height: 330 }}
    layers:
      - ellipse:
          color: {"red" if border_to_origin == "off" else "null"}
          arc: {{ end: -90 }}
          border:
            color: {"green" if border_to_origin == "on" else "null"}
            width: 45
          border_to_origin: {border_to_origin}
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()


@pytest.mark.parametrize(
    "sides",
    [
        2,
        pytest.param("[{ x: 100 }]", marks=pytest.mark.xfail),
        "[{ x: 100, y: -100 }, { x: 1230, y: 100 }, { x: 25, y: 25 }]",
    ],
    ids=["regular", "invalid_custom", "custom"],
)
def test_polygon(sphinx_make_app, sides: Union[int, str]) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="social_cards['enable']=False",
        files={
            "index.rst": f"""
Test Title
==========

.. social-card:: {{ "debug": true }}

    size: {TEST_AREA}
    layers:
      - polygon:
          color: green
          sides: {sides}
          border:
            width: 2
            color: blue
""",
        },
    )
    app.build()
    assert not app._warning.getvalue()
