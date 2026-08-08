Customized Layouts
==================

Layouts are written in YAML syntax. Before starting to create a custom layout, it is a good idea
to study :ref:`the pre-designed layouts <pre-designed-layouts>`, to get a better
understanding of how they work. Then, create a new layout and reference it in the
`social_cards <Social_Cards>` conf.py option (or within the :rst:dir:`social-card` directive's argument).

.. md-tab-set::

    .. md-tab-item:: ``layouts/custom.yml``

        .. code-block:: yaml
            :caption: ``layouts/custom.yml`` is located adjacent to conf.py file

            size: { width: 1200, height: 630 }
            layers: []

    .. md-tab-item:: ``conf.py``

        .. code-block:: python

            social_cards = { # (1)!
                "cards_layout_dir": "layouts",
                "cards_layout": "custom"
            }

        .. code-annotations::
            1. The required `site_url <Social_Cards.site_url>` is elided here for brevity.

    .. md-tab-item:: directive argument

        .. code-block:: rst

            .. social-card:: {
                    "cards_layout_dir" = "layouts",
                    "cards_layout" = "custom",
                }

Card Layout Options
*********************

.. autoclass:: sphinx_social_cards.validators.Cards_Layout_Options
    :members:

Layout Attributes
~~~~~~~~~~~~~~~~~

.. py:class:: Layout

    The `Layout.size` attribute is not required (see `width <Size.width>` and
    `height <Size.height>` for default values), but the :attr:`layers` attribute is
    required.

    Each layout supports these options:

    .. py:attribute:: size
        :type: Size

        The card's absolute maximum `size <Size>`. Any :attr:`layers` with no
        `size <Size>` specified will fallback to this :attr:`layout.size <Layout.size>`.
        If this is not specified, then the layout uses the default `width <Size.width>` and
        `height <Size.height>` values.

    .. py:attribute:: layers
        :type: list[Layer]

        A YAML list of :doc:`layers in the layout <layers>` that define the entire
        content of the layout.

Positioning Attributes
**********************

The layout's and individual layer's `size <Size>` and the individual layer's `offset <Offset>` are
defined in pixels. The size is defined by a `width <Size.width>` and `height <Size.height>`
property, and the offset is defined by `x <Offset.x>` and `y <Offset.y>` properties:

.. social-card:: {"debug":true}
    :dry-run:
    :hide-conf:

    size: { width: 300, height: 300 } # the layout maximum size
    layers:  # each layer in this list is denoted with a dash ('-')
      - {}
      - size: { width: 240, height: 240 }
        offset: { x: 30, y: 30 }

The layer outline and grid are visible because we enabled `debug <Social_Cards.debug>` in the
`social_cards <Social_Cards>` configuration. The rest of the image is transparent because there
are no layers with any actual content specified (like `background <Background>`, `icon <Icon>` or
`typography <Typography>`).

Upon closer inspection you'll notice that

- layer :yaml:`0` uses the layout's `size <Size>` and the default `offset <Offset>`
- layer :yaml:`1` uses a specified `size <Size>` and `offset <Offset>`


.. py:class:: Size

    An attribute to describe a layer's or layout's size.

    .. py:attribute:: width
        :type: int
        :value: 1200

        The width of the layer (relative to the `offset <Offset>`).
        Defaults to 1200 pixels width.

    .. py:attribute:: height
        :type: int
        :value: 630

        The height of the layer (relative to the `offset <Offset>`).
        Defaults to 630 pixels height.

.. py:class:: Offset

    An attribute to describe a layer's positional offset.

    .. py:attribute:: x
        :type: int
        :value: 0

        The offset on the X axis (relative to the top-left corner of the card). Defaults
        to 0.

    .. py:attribute:: y
        :type: int
        :value: 0

        The offset on the Y axis (relative to the top-left corner of the card). Defaults
        to 0.
