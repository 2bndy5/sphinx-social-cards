Layer Ellipse attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: Ellipse

    This layer attribute renders an ellipse using the layer's size and offset
    to define the outlining bounding box.

    .. md-tab-set::

        .. md-tab-item:: only border

            .. social-card:: { "debug": {"enable": true, "grid": false} }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: '#4051B2' }
                  - ellipse:
                      border:
                        width: 50
                        color: red
                    size: { width: 500, height: 300 }
                    offset: { x: 350, y: 165 }

        .. md-tab-item:: only fill

            .. social-card:: { "debug": {"enable": true, "grid": false} }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: '#4051B2' }
                  - ellipse:
                      color: green
                    size: { width: 300, height: 500 }
                    offset: { x: 450, y: 65 }

        .. md-tab-item:: border and fill

            .. social-card:: { "debug": {"enable": true, "grid": false} }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: '#4051B2' }
                  - ellipse:
                      border:
                        width: 50
                        color: red
                      color: green
                    size: { width: 400, height: 400 }
                    offset: { x: 400, y: 115 }

    .. py:attribute:: arc
        :type: Arc | None

        The specification for drawing only an `arc <Arc>` of an ellipse.

    .. py:attribute:: border_to_origin
        :type: bool
        :value: False

        This switch controls the rendering of the border when :attr:`arc` is specified.
        If the :attr:`arc` attribute is not specified, then this switch has no effect.

        By default (:yaml:`false`), the border is not drawn between the arc endpoints and
        the angle's origin -- meaning only the arc itself has a border. Set this to
        :yaml:`true` to render the border between arc endpoints.

        .. jinja::

            .. md-tab-set::

                {% for switch in ['on', 'off'] %}

                .. md-tab-item:: :yaml:`border_to_origin: {{ switch }}`

                    .. social-card:: { "debug": {"enable": true, "grid": false} }
                        :dry-run:
                        :hide-conf:

                        layers:
                          - background: { color: '#4051B2' }
                          - ellipse:
                              border_to_origin: {{ switch }} {% if switch == 'off' -%}
                              # this is the default if not specified{% endif %}
                              arc: { start: 0, end: 135 }
                              color: red
                              border: { width: 25, color: green }
                            size: { width: 500, height: 300 }
                            offset: { x: 350, y: 165 }
                {% endfor %}

    .. py:attribute:: border
        :type: Border

        The shape's outlining `border <Border>` specification.

    .. py:attribute:: color
        :type: str | None

        The shape's fill color.

        .. seealso:: Please review :ref:`choosing_a_color` section for more detail.

.. py:class:: Arc

    This attribute allows specifying starting and ending angles that render as an
    arc of a circle.

    .. important::
        The angle of origin (0 degrees) is 3 o'clock and increases clockwise.
    .. jinja::

        .. md-tab-set::

            {% for start, end in [(45, 135), (135, 225), (225, 315), (315, 45)] %}

            .. md-tab-item:: :yaml:`arc: { start: {{ start }}, end: {{ end }} }`

                .. social-card:: { "debug": {"enable": true, "grid": false} }
                    :dry-run:
                    :hide-conf:

                    layers:
                      - background: { color: '#4051B2' }
                      - ellipse:
                          arc: { start: {{ start }}, end: {{ end }} }
                          border: { width: 20, color: red }
                          border_to_origin: on
                        size: { width: 500, height: 300 }
                        offset: { x: 350, y: 165 }
            {% endfor %}

    .. py:attribute:: start
        :type: float
        :value: 0

        The starting angle.

    .. py:attribute:: end
        :type: float
        :value: 0

        The ending angle.
