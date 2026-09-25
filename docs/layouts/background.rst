Layer Background attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: Background

    When combining these attributes, the `Background.image` is tinted with the `Background.color`.

    .. hint::
        If no alpha transparency is included with the specified `Background.color`, then the
        `Background.color` will block out the `Background.image`.
    .. social-card::
        :dry-run:

        layers:
          - background:
              image: images/rainbow.png
              color: "#000000AB"

    .. py:attribute:: image
        :type: str | None

        The path to an image used as the card's background. This path can be absolute or
        relative to one of the paths specified in
        `social_cards.image_paths <Social_Cards.image_paths>`.

        .. failure:: Missing file extensions

            If the image file's name does not include a file extension (eg ``.png``), then
            it is assumed to ba a SVG image (``.svg`` is appended to the filename).

        By default, this image will be resized to fit within the layer's `size <Size>`. See
        `preserve_aspect <Background.preserve_aspect>` for more details on resizing images.

        .. social-card::
            :dry-run:

            layers:
              - background:
                  image: images/rainbow.png

    .. py:attribute:: color
        :type: str | None

        The color used as the background fill color. This color will overlay the entire
        `background.image <Background.image>` (if specified). So be sure to add transparency
        (an alpha color value) when using both a background image and color.

        .. seealso:: Please review :ref:`choosing_a_color` section for more detail.

        .. social-card::
            :dry-run:

            layers:
              - background:
                  color: "#4051b5"

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
