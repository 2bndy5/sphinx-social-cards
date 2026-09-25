Radial Gradients
================

.. py:class:: Radial_Gradient

    A specification for radial gradients of colors.

    .. py:attribute:: center
        :type: Offset

        The starting position (`offset <Offset>`) relative to the layout's `offset <Offset>`
        (the absolute top-left corner of the card). This offset corresponds to the minimum
        ``0.0`` position in the mapping of `Radial_Gradient.colors`.

    .. py:attribute:: radius
        :type: float

        The radius represents the ending position as a distance (in pixels) from the
        specified `Radial_Gradient.center` `offset <Offset>`. The resulting circumference corresponds to the
        maximum ``1.0`` position in the mapping of `Radial_Gradient.colors`.

        .. warning::
            This radius *must* be a greater than 0.

        .. jinja::

            .. md-tab-set::

                {% for radius in [50, 100, 200, 250] %}

                .. md-tab-item:: :yaml:`radius: {{ radius }}`

                    .. social-card::
                        :dry-run:

                        size: { height: 400, width: 400 }
                        layers:
                          - background:
                              radial_gradient:
                                center: { x: 200, y: 200 }
                                radius: {{ radius }}
                                colors:
                                  0.0: red
                                  # show the end of the radius by setting color at
                                  # maximum position to the background color
                                  0.9999: green
                                  1.0: blue
                {% endfor %}

    .. py:attribute:: focal_point
        :type: Offset | None

        The focal point (`offset <Offset>`) used to give the gradient a perspective.
        By default, the value of `Radial_Gradient.center` is used. If the specified `offset <Offset>` is
        outside the circumference defined via `Radial_Gradient.radius`, then this `offset <Offset>` will
        be moved to the outer-most point on the circle that would be formed by the `Radial_Gradient.radius`
        from the `Radial_Gradient.center`.

        .. jinja::

            .. md-tab-set::

                {% for i in range(2) %}
                {% if not i %}
                {% set point = 'focal_point: { x: 100, y: 100 }' %}
                {% else %}
                {% set point = 'focal_point: null' %}
                {% endif %}

                .. md-tab-item:: :yaml:`{{ point }}`

                    .. social-card::
                        :dry-run:

                        size: { height: 400, width: 400 }
                        layers:
                          - background: { color: blue }
                          - ellipse:
                              radial_gradient:
                                center: { x: 200, y: 200 }
                                radius: 200
                                {{ point }}  {% if i -%}
                                # the default (uses center offset){% endif %}
                                colors:
                                  0.0: red
                                  1.0: green
                {% endfor %}

    .. py:attribute:: focal_radius
        :type: float | None

        The radius from the `focal_point` defines the aperture width of the gradient's
        perspective. This is highly relative to the `Radial_Gradient.center`'s `Radial_Gradient.radius`. Furthermore, if the
        `focal_radius` forms a circumference than extends beyond the `Radial_Gradient.center`'s `Radial_Gradient.radius`,
        then the gradient is effectively nullified and treated like a solid color (which
        coincides with the `Radial_Gradient.colors` list maximum position, 1.0).

        .. example:: Using :yaml:`spread: repeat` as a proof

            The following example uses the :yaml:`repeat` `Radial_Gradient.spread` to show the
            `focal_radius` area. Remember that the :yaml:`repeat` `Radial_Gradient.spread` effectively
            repeats the gradient outside the gradient's effected area (using the same order
            of `Radial_Gradient.colors`).

        .. jinja::

            .. md-tab-set::

                {% for radius in [-100, 0, 50, 58] %}

                .. md-tab-item:: :yaml:`focal_radius: {{ radius }}`

                    .. social-card::
                        :dry-run:

                        size: { height: 400, width: 400 }
                        layers:
                          - background: { color: blue }
                          - ellipse:
                              radial_gradient:
                                center: { x: 200, y: 200 }
                                radius: 200
                                focal_radius: {{ radius }} {% if radius == 0 -%}
                                # the default value if not specified{% endif %}
                                focal_point: { x: 100, y: 100 }
                                colors:
                                  0.0: red
                                  1.0: green
                                spread: repeat
                {% endfor %}

    .. py:attribute:: preset
        :type: str | int | None

        An optional preset gradient that has a pre-defined mapping of `Radial_Gradient.colors`. Each
        preset is referenced by name (string) or by index (integer). See the :doc:`presets`
        document for a complete list of supported values (with generated examples).

        .. social-card::
            :dry-run:

            layers:
              - background:
                  radial_gradient:
                    preset: PhoenixStart
                    # or equivalently
                    preset: 82
                    center: { x: 600, y: 315 }
                    radius: 600

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
        a `Radial_Gradient.preset`, then this mapping will override colors in the preset's mapping of
        colors. When neither the `Radial_Gradient.preset` or `Radial_Gradient.colors` is specified, this defaults to
        :yaml:`0.0: black` and :yaml:`1.0: white`.

        .. |gradient_positions| replace:: `Radial_Gradient.center` and `Radial_Gradient.radius`

        .. social-card::
            :dry-run:

            layers:
              - background:
                  radial_gradient:
                    colors:
                      0.0: red
                      0.5: green
                      1.0: blue
                    center: { x: 600, y: 315 }
                    radius: 600

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
                              radial_gradient:
                                spread: {{ spread }}
                                colors:
                                  0.0: red
                                  0.5: green
                                  1.0: blue
                                center: { x: 600, y: 315 }
                                radius: 300
                {% endfor %}
