Linear Gradients
================

.. py:class:: Linear_Gradient

    A specification for linear gradients of colors.

    .. py:attribute:: start
        :type: Offset

        The starting position (`offset <Offset>`) relative to the layout's `offset <Offset>`
        (the absolute top-left corner of the card). This offset corresponds to the minimum
        ``0.0`` position in the mapping of `Linear_Gradient.colors`.

    .. py:attribute:: end
        :type: Offset

        The ending position (`offset <Offset>`) relative to the layout's `offset <Offset>`
        (the absolute top-left corner of the card). This offset corresponds to the maximum
        ``1.0`` position in the mapping of `Linear_Gradient.colors`.

    .. py:attribute:: preset
        :type: str | int | None

        An optional preset gradient that has a pre-defined mapping of `Linear_Gradient.colors`. Each
        preset is referenced by name (string) or by index (integer). See the :doc:`presets`
        document for a complete list of supported values (with generated examples).

        .. social-card::
            :dry-run:

            layers:
              - background:
                  linear_gradient:
                    preset: PhoenixStart
                    # or equivalently
                    preset: 82
                    start: { x: 60, y: 60 }
                    end: { x: 1140, y: 570 }

    .. py:attribute:: colors
        :type: dict

        A mapping of colors to their corresponding positions in the gradient.
        Each item in this mapping is composed of :yaml:`key: value` pairs in which:

        - The :yaml:`key:` is a position at which the color will occur in the gradient.
          This `float` *must* be in the range ``0`` to ``1`` inclusively. More detail about
          how these positional values are used is described in |gradient_positions|.
        - The :yaml:`value` is a :ref:`solid color <solid_color>` to use at the specified
          point in the gradient.

        This mapping's color positions does not have to be in any specific order. If using
        a `Linear_Gradient.preset`, then this mapping will override colors in the preset's mapping of
        colors. When neither the `Linear_Gradient.preset` or `Linear_Gradient.colors` is specified, this defaults to
        :yaml:`0.0: black` and :yaml:`1.0: white`.

        .. |gradient_positions| replace:: `Linear_Gradient.start` and `Linear_Gradient.end`

        .. social-card::
            :dry-run:

            layers:
              - background:
                  linear_gradient:
                    colors:
                      0.0: red
                      0.5: green
                      1.0: blue
                    start: { x: 60, y: 60 }
                    end: { x: 1140, y: 570 }

    .. py:attribute:: spread
        :type: str
        :value: "pad"

        This attribute controls the colors' behavior outside the gradient's specified
        area. By default this is set to :yaml:`pad`.

        .. jinja::

            .. md-tab-set::

                {% for spread in ['pad', 'reflect', 'repeat'] %}

                .. md-tab-item:: :yaml:`spread: {{ spread }}`

                    .. social-card::
                        :dry-run:

                        layers:
                          - background:
                              linear_gradient:
                                spread: {{ spread }}
                                colors:
                                  0.0: red
                                  0.5: green
                                  1.0: blue
                                start: { x: 60, y: 315 }
                                end: { x: 600, y: 315 }
                {% endfor %}
