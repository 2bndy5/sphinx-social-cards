Layer Typography Attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: Typography

    .. py:attribute:: content
        :type: str

        The text to be displayed. This can be a |Jinja syntax| that has access to the
        card's `jinja contexts <jinja-ctx>`.

        The text content is pre-processed (after parsed from |Jinja syntax|) to allow
        comprehensive wrapping of words. This is beneficial for long winded programmatic
        names.

        .. caution::
            Beware that leading and trailing whitespace is stripped from each line.

        .. md-tab-set::

            .. md-tab-item:: Long words

                .. social-card:: {"debug": {"enable": true, "grid": false }}
                    :dry-run:
                    :hide-conf:
                    :hide-layout:
                    :meta-data: {
                      "title":
                        "sphinx_social_cards.validators.LayerTypographyDataclass._fg_color"}
                    :meta-data-caption: Using an API name as the page title

                    layers:
                      - background: { color: '#4051B2' }
                      - size: { width: 1080, height: 360 }
                        offset: { x: 60, y: 150 }
                        typography:
                          content: '{{ page.meta.title }}'
                          color: '{{ layout.color | yaml }}'
                          line: { amount: 4, height: 1.1 }
                          font: { family: Roboto Mono }

            .. md-tab-item:: Preserved line breaks

                .. note:: Line breaks are not supported when using :ref:`metadata-fields`.

                .. social-card:: {"debug": {"enable": true, "grid": false }}
                    :dry-run:
                    :layout-caption: Using a line break between words
                    :hide-conf:

                    layers:
                      - background: { color: '#4051B2' }
                      - size: { width: 1080, height: 360 }
                        offset: { x: 60, y: 150 }
                        typography:
                          content: |
                            Paragraph 1

                                Line with leading spaces
                          color: '{{ layout.color | yaml }}'
                          line: { amount: 3 }

    .. py:attribute:: align
        :type: str
        :value: "start top"

        The alignment of text used. This is a string in which the space-separated words
        respectively describe the horizontal and vertical alignment.

        .. list-table:: Alignment Options

            - * :si-icon:`material/arrow-top-left` ``start top``
              * :si-icon:`material/arrow-up` ``center top``
              * :si-icon:`material/arrow-top-right` ``end top``
            - * :si-icon:`material/arrow-left` ``start center``
              * :si-icon:`material/circle-small` ``center`` or ``center center``
              * :si-icon:`material/arrow-right` ``end center``
            - * :si-icon:`material/arrow-bottom-left` ``start bottom``
              * :si-icon:`material/arrow-down` ``center bottom``
              * :si-icon:`material/arrow-bottom-right` ``end bottom``

    .. py:attribute:: color
        :type: str | None

        The color to be used for the displayed text. If not specified, then this defaults
        to `cards_layout_options.color <Cards_Layout_Options.color>`.

        .. seealso:: Please review :ref:`choosing_a_color` section for more detail.

    .. py:attribute:: line
        :type: Line

        The `line <Line>` specification which sets the `amount <Line.amount>` of lines
        and the `height <Line.height>` of each line. This is used to calculate the font's
        size.

    .. py:attribute:: overflow
        :type: bool
        :value: False

        Set this option to :yaml:`true` to automatically shrink the font size enough to
        fit within the layer's `size <Size>`. By default (:yaml:`false`), text will be
        truncated when the layer' capacity is reached, and an ellipsis will be added.

        .. jinja::

            .. md-tab-set::

            {% for desc in ["off", "on"] %}
                .. md-tab-item:: :yaml:`overflow: {{ desc }}`

                    .. social-card:: {"debug": {"enable": true, "grid": false }}
                        :dry-run:
                        :hide-layout:
                        :hide-conf:

                        layers:
                          - background: {color: "#4051b5"}
                          - offset: { x: 60, y: 150 }
                            size: { width: 832, height: 330 }
                            typography:
                              content: >
                                If we use a very long sentence, then we gleam how the text
                                will be truncated.
                              color: white
                              line:
                                amount: 3
                              {% if desc == 'on' -%}
                              overflow: true
                              {%- endif %}
              {% endfor %}

    .. py:attribute:: font
        :type: Font | None

        The specified font to use. If not specified, then this defaults to values in
        `cards_layout_options.font <Cards_Layout_Options.font>`.

        .. seealso:: Please review :ref:`choosing-a-font` section.

    .. py:attribute:: border
        :type: Border

        The `border <Border>` specification defines the behavior of rendering an outline
        around each character.

        .. seealso::
            This attribute shares the same `border <Border>` specification that is used by the
            supported :doc:`shapes/index`.
        .. important::
            If the `border.color <Border.color>` is not specified, then the
            `typography.color <Typography.color>` is used.

        .. social-card::
            :dry-run:
            :layout-caption: A stroke around transparent characters

            size: { width: 600, height: 110 }
            layers:
            - background: {color: "#4051b5"}
            - typography:
                content: Fancy Text
                color: '#00000000' # a transparent color
                align: center
                border:
                    width: 2
                    color: white

Typography Line specification
-----------------------------

.. py:class:: Line

    These properties are used to calculate the font's size based on the layer's
    absolute maximum `size <Size>`.

    .. py:attribute:: amount
        :type: int
        :value: 1

        The maximum number of lines that can be used in the layer.

    .. py:attribute:: height
        :type: float
        :value: 1

        The relative height allotted to each line. This has a direct affect on spacing
        between lines because each layer has an absolute maximum `size <Size>`.

        .. |height0.75| replace:: 75% of the appropriately available line
            height. Text will be smaller, but the layer's height will not be fully used.

        .. |height1| replace:: the full appropriately available line
            height. Text will be large enough to fit within of the appropriately available
            line height.

        .. |height1.25| replace:: 125% of the appropriately available line
            height. Text will be bigger but the space between lines will be smaller (can
            even be negative).

        .. |height2.0| replace:: 200% of the appropriately available line
            height. Text should never exceed the layer size, thus spacing between lines is
            adjusted accordingly.

        .. |height0.5| replace:: 50% of the appropriately available line
            height. Notice the line height is directly related to height of the layer.

        .. jinja::

            .. md-tab-set::

            {% for height in [0.75, 1, 1.25, 2.0, 0.5] %}
                .. md-tab-item:: :yaml:`height: {{ height }}`

                    :yaml:`{{ height }}` means each line can have |height{{ height }}|

                    .. social-card:: {"debug": {"enable": true, "grid": false }}
                        :dry-run:
                        :hide-layout:
                        :hide-conf:

                        layers:
                          - background: {color: "#4051b5"}
                          - offset: { x: 60, y: 150 }
                            size: { width: 832, height: 330 }
                            typography:
                              content: |
                                Typography
                                Glyphs
                                Pictograms
                              color: white
                              line:
                                amount: 3
                                height: {{ height }}
                              border: { width: {{ (height * 1.5) | round | int }}, color: red }
            {% endfor %}

Font specification
------------------

.. py:class:: Font

    The specification that describes the font to be used.

    .. seealso:: Please review the :ref:`choosing-a-font` section.

    .. py:attribute:: family
        :type: str
        :value: "Roboto"

        This option specifies which font to use for rendering the social card, which can
        be any font hosted by `Fontsource`_. Default is :python:`"Roboto"` if not using the
        sphinx-immaterial_ theme. However, the sphinx-immaterial theme's :themeconf:`font`
        option is used as a default if that theme is used.

        If the font specified is not a Roboto font and cannot be fetched from Fontsource_,
        then an exception is raised and the docs build is aborted.

    .. py:attribute:: style
        :type: str
        :value: "normal"

        The style of the font to be used. Typically, this can be ``italic`` or
        ``normal``, but it depends on the styles available for the chosen `family`.

        .. failure:: There is no inline style parsing.
            :collapsible:

            Due to the way fonts are loaded, there's no way to embed syntactic inline
            styles for individual words or phrases in the text content. ``**bold**`` and
            ``*italic*`` will not render as **bold** and *italic*.

            Instead, the layout customization could be used to individually layer stylized
            text.

    .. py:attribute:: weight
        :type: int
        :value: 400

        The weight of the font used. If this doesn't match the weights available, then
        the first weight defined for the font is used and a warning is emitted. Default is
        :yaml:`400`.

    .. py:attribute:: subset
        :type: str | None

        A subset type used for the font. If not specified, this will use the default
        defined for the font (eg. :python:`"latin"`).

    .. py:attribute:: path
        :type: str | None

        The path to the TrueType font (``*.ttf``). If this is not specified, then it is
        set in accordance with the a cache corresponding to the `family`, `style`, `weight`,
        and `subset` options. If explicitly specified, then this value overrides the
        `family`, `style`, `weight`, and `subset` options.
