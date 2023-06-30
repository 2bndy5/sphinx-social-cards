import pytest
from sphinx.testing.util import SphinxTestApp


@pytest.mark.parametrize(
    "style", ["normal", pytest.param("bold", marks=pytest.mark.xfail)]
)
@pytest.mark.parametrize("weight", [400, 555])
@pytest.mark.parametrize(
    "subset", ["latin", pytest.param("undefined", marks=pytest.mark.xfail)]
)
def test_font(sphinx_make_app, style: str, weight: int, subset: str):
    app: SphinxTestApp = sphinx_make_app(
        extra_conf=f"""html_theme = 'furo'
social_cards["cards_layout_options"] = {{
    "font": {{
        "family": "Noto Sans",
        "style": '{style}',
        "weight": {weight},
        "subset": '{subset}',
    }}
}}
""",
        files={
            "index.rst": """
A Really Long Test Title That Overflows 2 Lines
===============================================

.. image-generator::

    layers:
      - size: { width: 1080, height: 210 }
        offset: { x: 60, y: 180 }
        typography:
          content: '{{ page.title }}'
          line: { amount: 2 }
"""
        },
    )
    app.build()
    assert not app._warning.getvalue()
