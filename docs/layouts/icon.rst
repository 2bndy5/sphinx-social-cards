Layer Icon Attribute
~~~~~~~~~~~~~~~~~~~~

.. py:class:: Icon

    When combining these attributes, the `Icon.image` is colorized by the specified
    `Icon.color`.

    .. hint:: If no `Icon.color` is specified, then the `Icon.image`\\ 's original color is shown.
    .. social-card::
        :dry-run:

        layers:
          - background: { color: "#4051B5" }
          - size: { width: 150, height: 150 }
            offset: { x: 525, y: 240 }
            icon:
              image: simple/sphinx
              color: "white"

    .. py:attribute:: image
        :type: str | None

        An image file's path. This path can be absolute or relative to one of the paths
        specified in `social_cards.image_paths <Social_Cards.image_paths>`.

        By default, this image will be resized to fit within the layer's `size <Size>`. See
        `preserve_aspect <Icon.preserve_aspect>` for more details on resizing images.

        .. failure:: Missing file extensions

            If the image file's name does not include a file extension (eg ``.png``), then
            it is assumed to ba a SVG image (``.svg`` is appended to the filename).
        .. note::
            If no :attr:`color` is specified, then the image's original color will be shown.
            For SVG images without hard-coded color information, black will be used.

        .. social-card::
            :dry-run:

            layers:
              - background: { color: "#4051B5" }
              - size: { width: 150, height: 150 }
                offset: { x: 525, y: 240 }
                icon:
                  image: simple/sphinx

    .. py:attribute:: color
        :type: str | None

        The color used as the fill color. The actual image color is not used when
        specifying this, rather the non-transparent data is used as a mask for this value.

        .. seealso:: Please review :ref:`choosing_a_color` section for more detail.

        .. hint::
            If an alpha transparency is included with the specified `Icon.color`, then the
            `Icon.image` will become transparent as well.

        .. social-card::
            :dry-run:

            layers:
              - background: { color: "#4051B5" }
              - size: { width: 150, height: 150 }
                offset: { x: 525, y: 240 }
                icon:
                  image: simple/sphinx
                  color: "#0000003F"

    .. py:attribute:: preserve_aspect
        :type: bool | str
        :value: True

        If an image is used that doesn't match the layer's `size <Size>`, then the image
        will be resized accordingly. This option can be used to control which horizontal
        `width <Size.width>` or vertical `height <Size.height>` or both (:yaml:`true`)
        constraints are respected. Set this option to :yaml:`false` to disable resizing the
        image. By default, this option is set to :yaml:`true`.

        If the image has to be resized then it is centered on the layer for which it is
        used.
