"""This module contains validating dataclasses for a parsed yaml layout."""
from typing import List, Optional

from pydantic import BaseModel
from .common import CustomBaseModel, Offset
from .layers import (
    Background,
    Icon,
    Typography,
    Ellipse,
    Rectangle,
    Polygon,
    PositiveInt,
)


class Size(CustomBaseModel):
    """An attribute to describe a layer's or layout's size."""

    width: PositiveInt = 1200
    """The width of the layer (relative to the `offset <Offset>`).
    Defaults to 1200 pixels width."""
    height: PositiveInt = 630
    """The height of the layer (relative to the `offset <Offset>`).
    Defaults to 630 pixels height."""

    def __gt__(self, other: "Size") -> bool:
        if not isinstance(other, Size):
            raise NotImplementedError(
                f"Cannot compare a Size object with {type(other)}"
            )
        return any([self.width > other.width, self.height > other.height])

    def __lt__(self, other: "Size") -> bool:
        if not isinstance(other, Size):
            raise NotImplementedError(
                f"Cannot compare a Size object with {type(other)}"
            )
        return any([self.width < other.width, self.height < other.height])

    def __eq__(self, other: "Size") -> bool:  # type: ignore[override]
        if not isinstance(other, Size):
            raise NotImplementedError(
                f"Cannot compare a Size object with {type(other)}"
            )
        return (self.width == other.width) and (self.height == other.height)

    def __ge__(self, other: "Size") -> bool:
        if not isinstance(other, Size):
            raise NotImplementedError(
                f"Cannot compare a Size object with {type(other)}"
            )
        return self > other or self == other

    def __le__(self, other: "Size") -> bool:
        if not isinstance(other, Size):
            raise NotImplementedError(
                f"Cannot compare a Size object with {type(other)}"
            )
        return (self < other) or (self == other)


class Layer(CustomBaseModel):
    """Each layer can have different attributes. A typical layer has :attr:`size` and
    :attr:`offset` attributes with 1 additional attribute detailing a
    :attr:`background` or :attr:`icon` or :attr:`typography` or :attr:`rectangle` or
    :attr:`ellipse`. However, these attributes may combined as needed.

    Each attribute has a priority, so using multiple attributes on a single layer
    will render consistently. The priority order is as follows (excluding
    :attr:`size` and :attr:`offset`):

    1. :attr:`background`
    #. :attr:`rectangle`
    #. :attr:`ellipse`
    #. :attr:`polygon`
    #. :attr:`icon`
    #. :attr:`typography`
    #. :attr:`mask`

    Meaning, any :attr:`background` attribute is always rendered before other layer
    attributes. Additionally, any :attr:`typography` attribute is rendered after
    other attributes but before applying the :attr:`mask`.

    .. social-card::
        :dry-run:
        :layout-caption: A layout with a single layer that has multiple attributes

        size: { width: 200, height: 200 }
        layers:
          - typography: # the layer's typography attribute
              content: "S"
              align: center
            background: # the layer's background attribute
              color: '{{ layout.background_color | yaml }}'
            icon: # the layer's icon attribute
              image: '{{ layout.logo.image }}'

        # NOTE that the order of layer attributes does not matter

    .. error::
        Each layer can only have 1 of each type of attribute. For example you cannot use
        2 :attr:`background` attributes in a single layer:

        .. social-card::
            :dry-run:

            size: { width: 600, height: 250 }
            layers:
              - background: { image: 'images/rainbow.png' }
                # The `background` attribute is overwritten by next line
                background: { color: '#ff000037' }

            # NOTE: The layer's background attribute is composed solely by
            # the last instance of the background attribute in the layer.
    """

    #: An optional :doc:`background`.
    background: Optional[Background] = None
    #: An optional :doc:`typography`.
    typography: Optional[Typography] = None
    #: An optional :doc:`shapes/rectangle`.
    rectangle: Optional[Rectangle] = None
    #: An optional :doc:`shapes/ellipse`.
    ellipse: Optional[Ellipse] = None
    #: An optional :doc:`shapes/polygon`.
    polygon: Optional[Polygon] = None
    #: An optional :doc:`icon`.
    icon: Optional[Icon] = None
    size: Optional[Size] = None
    """The layer `size <Size>`. Defaults to values inherited from the
    `layout.size <Layout.size>`."""
    #: The layer `offset <Offset>`. Defaults to :yaml:`{ x: 0, y: 0 }`.
    offset: Offset = Offset()
    #: An optional :doc:`mask`.
    mask: Optional["Mask"] = None


class Mask(Layer):
    """If specified, this attribute will define a bump mask. This value can only be 1
    `layer <Mask>` with an optional `invert` attribute. Any transparent part of the
    `mask <Mask>` layer will be removed from the current `layer <Layer>` for which the
    `mask <Mask>` is defined.

    This attribute that can be used as a cropping mechanism.

    .. important::
        :title: Meaning of a mask layer's Size and Offset

        Where "current layer" is the layer in which the `mask <Layer.mask>` attribute is
        set:

        - The mask layer's `offset <Offset>` is relative the current layer's `offset
          <Offset>`.
        - The resulting mask layer's `size <Size>` (after rendering) is expanded or
          cropped to the current layer's `size <Size>`.

    .. md-tab-set::

        .. md-tab-item:: Text as a mask

            .. social-card::
                :dry-run:

                layers:
                  - background: { color: "#4051B2" }
                  - background: { image: images/rainbow.png }
                    mask:
                      typography:
                        content: This string was used as a mask.
                        line:
                          height: 1.2
                          amount: 3
                        align: center

        .. md-tab-item:: Text as a layer

            .. social-card::
                :dry-run:

                layers:
                  - background: { color: "#4051B2" }
                  - typography:
                      content: This string was used as a mask.
                      line:
                        height: 1.2
                        amount: 3
                      align: center

        .. md-tab-item:: Rectangle as a mask

            .. social-card::
                :dry-run:

                layers:
                  - background: { color: "#4051B2" }
                  - background: { image: images/rainbow.png }
                    mask:
                      size: { width: 600, height: 315 }
                      offset: { x: 300, y: 158 }
                      rectangle:
                        color: '#FFFFFF3F' # a transparent color
                        radius: 100
                        border:
                          width: 50
                          color: white

        .. md-tab-item:: Rectangle as a layer

            .. social-card::
                :dry-run:

                layers:
                  - background: { color: '#4051B2' }
                  - size: { width: 600, height: 315 }
                    offset: { x: 300, y: 158 }
                    rectangle:
                      color: '#FFFFFF3F' # a transparent color
                      radius: 100
                      border:
                        width: 50
                        color: white
    """

    invert: bool = False
    """Use this `bool` attribute to cause the mask layer's transparency to become
    inverted. This is only useful if excluding pixels from the layer's image is desired.

    .. jinja::

        .. md-tab-set::

            .. md-tab-item:: Excluding an image

                .. social-card::
                    :dry-run:

                    layers:
                      - background: { color: '#4051B2' }
                      # this red background is drawn to prove the transparency of the mask
                      - background: { color: red }
                        offset: { x: 600 }
                      - size: { width: 200, height: 200 }
                        offset: { x: 500, y: 215 }
                        rectangle:
                          color: green
                          radius: 50
                        mask:
                          invert: true
                          size: { width: 150, height: 150 }
                          offset: { x: 25, y: 25 }
                          icon: { image: 'sphinx_logo' }

            {% for offset in ['negative', 'same', 'positive'] %}
            .. md-tab-item:: Excluding with {{ offset }} offset

                .. social-card::
                    :dry-run:

                    layers:
                      - background: { color: '#4051B2' }
                      - background: { color: white }
                        offset: { x: 450, y: 150 }
                        size: { width: 300, height: 300 }
                        mask:
                          invert: true
                          size: { width: 300, height: 300 }
                          {% if offset != 'same' -%}
                          offset: { x: {% if offset == 'negative' %}-{% endif %}150 }
                          {%- endif %}
                          ellipse: { color: '#0000003f' }
            {% endfor %}
    """


# we must do this since the Layer has a Mask attribute whose type inherits from Layer
Layer.model_rebuild()


class Layout(BaseModel):
    """The `size` attribute is not required (see `width <Size.width>` and
    `height <Size.height>` for default values), but the :attr:`layers` attribute is
    required.

    Each layout supports these options:
    """

    size: Size = Size()
    """The card's absolute maximum `size <Size>`. Any :attr:`layers` with no
    `size <Size>` specified will fallback to this :attr:`layout.size <Layout.size>`.
    If this is not specified, then the layout uses the default `width <Size.width>` and
    `height <Size.height>` values.
    """
    layers: List[Layer] = []
    """A YAML list of :doc:`layers in the layout <layers>` that define the entire
    content of the layout."""
