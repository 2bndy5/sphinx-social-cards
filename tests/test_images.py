from sphinx.testing.util import SphinxTestApp


def test_icon_gradient_overlay(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        files={
            "index.rst": """
Test Title
==========

.. image-generator::

    size: { width: 250, height: 250 }
    layers:
      - background: { color: black }
      - icon:
          image: sphinx_logo
          conical_gradient:
            preset: 5 # "YoungPassion"
            center: { x: 125, y: 125 }
            radius: 125
"""
        },
    )

    app.build()
    assert not app._warning.getvalue()  # type: ignore[attr-defined]
