from pathlib import Path
from typing import Optional, Union, Literal

from sphinx.testing.util import SphinxTestApp
from PySide6.QtGui import QImage
import pytest
from sphinx_social_cards.images import resize_image, get_embedded_svg
from sphinx_social_cards.validators.layout import Size


@pytest.mark.parametrize(
    "image",
    [
        None,
        pytest.param(__file__, marks=pytest.mark.xfail),
        Path(__file__).parent.parent / "docs" / "images" / "avatar.jpg",
        Path(__file__).parent.parent / "docs" / "images" / "rainbow.png",
        Path(__file__).parent / "rainbow.png",
        "material/library",
        "fontawesome/solid/language",
        "fontawesome/regular/building",
        "simple/python",
    ],
    ids=[
        "none",
        "invalid",
        "square_jpg",
        "wide_png",
        "tall_png",
        "square_svg",
        "wide_svg",
        "tall_svg",
        "same_size",
    ],
)
@pytest.mark.parametrize("size", [Size(width=100, height=100)])
@pytest.mark.parametrize("aspect_ratio", [True, "width", "height"])
def test_resize_image(
    image: Optional[Union[str, Path]],
    size: Size,
    aspect_ratio: Union[bool, Literal["width", "height"]],
):
    path = image
    if isinstance(image, str) and "/" in image and image != __file__:
        pack, slug = image.split("/", maxsplit=1)
        path = get_embedded_svg(pack, slug)
    result = resize_image(path, size, aspect_ratio)
    if result:
        assert isinstance(result, QImage)
        assert result.width() == size.width
        assert result.height() == size.height


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
    assert not app._warning.getvalue()
