Conical Gradients
=================

.. py:class:: Conical_Gradient

    A specification for conical gradients of colors.

    .. failure:: ``spread`` not applicable to conical gradients

        Conceptually, the ``spread`` feature of other gradients can not be applied to
        conical gradients because conical gradients are implemented using the polar
        coordinate system.

    .. py:attribute:: center
        :type: Offset

        The starting position (`offset <Offset>`) relative to the layout's `offset <Offset>`
        (the absolute top-left corner of the card). This offset corresponds to the minimum
        ``0.0`` position in the mapping of `Conical_Gradient.colors`.

    .. py:attribute:: angle
        :type: float

        The angle of the the line from `Conical_Gradient.center` the represents the gradient's start and
        stop limits. This value (in degrees) is clamped to a value greater than or equal to
        0 and less than 360. The angle of origin (``0`` degrees) is located at 3 o'clock and
        increases counter-clockwise. The scale of listed `Conical_Gradient.colors` begins at ``0.0`` on this
        line and continues counter-clockwise until ending at ``1.0`` on this line.

        .. jinja::

            .. md-tab-set::

                {% for angle in [-45, 0, 45, 180] %}

                .. md-tab-item:: :yaml:`angle: {{ angle }}`

                    .. social-card::
                        :dry-run:

                        size: { height: 400, width: 400 }
                        layers:
                          - ellipse:
                              conical_gradient:
                                center: { x: 200, y: 200 }
                                angle: {{ angle }}
                                colors:
                                  0.0: red
                                  0.5: green
                                  1.0: blue
                {% endfor %}

    .. py:attribute:: preset
        :type: str | int | None

        An optional preset gradient that has a pre-defined mapping of `Conical_Gradient.colors`. Each
        preset is referenced by name (string) or by index (integer). See the :doc:`presets`
        document for a complete list of supported values (with generated examples).

        .. social-card::
            :dry-run:

            layers:
              - background:
                  conical_gradient:
                    preset: PhoenixStart
                    # or equivalently
                    preset: 82
                    center: { x: 600, y: 315 }
                    angle: 27.5

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
        a `Conical_Gradient.preset`, then this mapping will override colors in the preset's mapping of
        colors. When neither the `Conical_Gradient.preset` or `Conical_Gradient.colors` is specified, this defaults to
        :yaml:`0.0: black` and :yaml:`1.0: white`.

        .. |gradient_positions| replace:: `Conical_Gradient.center` and `angle`

        .. social-card::
            :dry-run:

            layers:
              - background:
                  conical_gradient:
                    colors:
                      0.0: red
                      0.5: green
                      1.0: blue
                    center: { x: 600, y: 315 }
                    angle: 27.5
