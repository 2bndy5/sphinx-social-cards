Layer Polygon attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: Polygon

    This layer attribute provides a way of drawing polygons with varying number of
    `sides`.

    .. note::
        The position of the polygon may not always be centered as it depends on the
        specification of `sides`.

    .. seealso::
        The size of the rendered polygon is constrained by how the `sides` are
        specified. Please review the 2 distinct ways to specify a polygon's `sides`.

    .. md-tab-set::

        .. md-tab-item:: Proof of regular polygon's occupied area

            .. social-card:: { "debug": {"enable": true, "grid": false} }
                :hide-conf:
                :dry-run:
                :layout-caption: The area of a regular polygon will never be larger than
                    the area of a circle within the layer.

                layers:
                  - background: { color: '#4051B2' }
                  - size: { width: 400, height: 400 } # size forms a perfect square
                    offset: { x: 400, y: 115 }
                    ellipse: # an ellipse to prove the maximum size of the polygon
                      border: { color: white, width: 4 }
                    polygon:
                      border: { width: 20, color: red }
                      color: green

        .. md-tab-item:: A rectangular layer size for a regular polygon

            .. social-card:: { "debug": {"enable": true, "grid": false} }
                :hide-conf:
                :dry-run:
                :layout-caption: The area of the regular polygon is determined by the
                    smallest value for the layer's width or height (if not equal).

                layers:
                  - background: { color: '#4051B2' }
                  - size: { width: 600, height: 400 } # size is not a perfect square
                    offset: { x: 300, y: 115 }
                    polygon:
                      sides: 6
                      border: { width: 20, color: red }
                      color: green

    .. py:attribute:: sides
        :type: int | list[Offset]
        :value: 3

        .. |offset-list| replace:: a YAML list of `offset <Offset>`\ s

        The specification of the polygon's sides. This can be an integer or
        |offset-list|.

        :Using an Integer (regular polygon):
            The number of sides that defines the edge of the polygon. This cannot be less
            than :yaml:`3` if specified as an integer.

            .. important::
                :title: Area of polygons are *restricted*

                If `sides` is an integer, then the rendered polygon *is* limited to the area
                of a circle within the layer. In this case, the layer's `size <Size>`
                determines the size of the polygon, but the layer `size <Size>` should form
                a perfect square to maximize the area that the polygon occupies. If the
                `size.width <Size.width>` and `size.height <Size.height>` are not equal,
                then the smaller of the two is used to limit the size of the polygon.

        :Using a YAML list of offsets (custom polygon):
            This can also be |offset-list| in which each specified `offset <Offset>` is a
            point relative to the top-left corner of the layer.

            .. important::
                :title: Area of polygons are *clamped*

                If any of the specified `offset <Offset>`\ s are located outside the
                layer's `size <Size>`, then the `offset <Offset>` will be moved to within
                the layer's `size <Size>`. This stipulation has a noticeable effect on
                polygons draw with a `border <Border>`.

        .. jinja::

            .. md-tab-set::

            {% for sides in [3, 6, 9] %}

                .. md-tab-item:: :yaml:`sides: {{ sides }}`

                    .. social-card:: { "debug": {"enable": true, "grid": false} }
                        :dry-run:
                        :hide-conf:

                        layers:
                          - background: { color: '#4051B2' }
                          - polygon:
                              sides: {{ sides }} {% if sides == 3 -%}
                              # this is the default if not specified{% endif %}
                              color: green
                              border:
                                width: 30
                                color: red
                            size: { width: 400, height: 400 }
                            offset: { x: 400, y: 115 }
            {% endfor %}
            {% for i in range(2) %}
            {% if not i %}
            {% set desc = 'with border' %}
            {% else %}
            {% set desc = 'without border' %}
            {% endif %}
                .. md-tab-item:: :yaml:`sides: [offset]` {{ desc }}

                    .. social-card:: { "debug": {"enable": true, "grid": false} }
                        :dry-run:
                        :hide-conf:

                        layers:
                          - background: { color: '#4051B2' }
                          - polygon:
                              sides:
                                - { x: 0, y: 400 } # bottom left
                                - { x: 200, y: 0 } # top center
                                - { x: 400, y: 400 } # bottom right
                              color: green
                              {% if not i -%}
                              border:
                                width: 30
                                color: red
                              {%- endif %}
                            size: { width: 400, height: 400 }
                            offset: { x: 400, y: 115 }
            {% endfor %}

    .. py:attribute:: rotation
        :type: float
        :value: 0

        The angles (in degrees) of arbitrary rotation (increasing counter-clockwise).

        .. error::
            If the `sides` attribute specifies |offset-list|, then any specified
            `rotation` is ignored (treated as :yaml:`0`).
        .. jinja::

            .. md-tab-set::

               {% for rotation in [0, 90, 180, 270, -45] %}

                .. md-tab-item:: :yaml:`rotation: {{ rotation }}`

                    .. social-card:: { "debug": {"enable": true, "grid": false} }
                        :dry-run:
                        :hide-conf:

                        layers:
                          - background: { color: '#4051B2' }
                          - polygon:
                              rotation: {{ rotation }} {% if not rotation -%}
                              # this is the default if not specified{% endif %}
                              color: green
                            size: { width: 400, height: 400 }
                            offset: { x: 400, y: 115 }
               {% endfor %}

    .. py:attribute:: border
        :type: Border

        The shape's outlining `border <Border>` specification.

    .. py:attribute:: color
        :type: str | None

        The shape's fill color.

        .. seealso:: Please review :ref:`choosing_a_color` section for more detail.
