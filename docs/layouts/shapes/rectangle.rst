Layer Rectangle attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. py:class:: Rectangle

    This layer attribute provides a way of drawing rectangles with rounded corners.

    .. md-tab-set::

        .. md-tab-item:: only border

            .. social-card:: { "debug": {"enable": true, "grid": false} }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: '#4051B2' }
                  - rectangle:
                      radius: 50
                      border:
                        width: 30
                        color: red
                    size: { width: 500, height: 300 }
                    offset: { x: 350, y: 165 }

        .. md-tab-item:: only fill

            .. social-card:: { "debug": {"enable": true, "grid": false} }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: '#4051B2' }
                  - rectangle:
                      radius: 50
                      color: green
                    size: { width: 300, height: 500 }
                    offset: { x: 450, y: 65 }

        .. md-tab-item:: border and fill

            .. social-card:: { "debug": {"enable": true, "grid": false} }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: '#4051B2' }
                  - rectangle:
                      radius: 50
                      border:
                        width: 30
                        color: red
                      color: green
                    size: { width: 400, height: 400 }
                    offset: { x: 400, y: 115 }

    .. py:attribute:: radius
        :type: int | float | None
        :value: 0

        The radius of the rounded corner in pixels. Defaults to 0 (no rounding).

        .. tip::
            If the `Rectangle.radius` is smaller than the half the `border.width <Border.width>`, then
            the border's inner `corners` will not be rounded.

        .. error::
            If the `Rectangle.radius` is more than half the of the rectangle's minimum width or height
            and not all `corners` are rounded, then there *will* be visible artifacts from
            rendering each corner individually.

    .. py:attribute:: corners
        :type: list[str]

        This YAML list of strings specifies which corners are rounded. By default all
        corners are rounded. The supported values are:

        .. list-table::

            * - :si-icon:`material/arrow-top-left` ``'top left'``
              - :si-icon:`material/arrow-top-right` ``'top right'``
            * - :si-icon:`material/arrow-bottom-left` ``'bottom left'``
              - :si-icon:`material/arrow-bottom-right` ``'bottom right'``

        .. social-card::
            :dry-run:

            layers:
              - background: { color: '#4051B2' }
              - size: { width: 100, height: 400 }
                offset: { x: 225, y: 115 }
                rectangle:
                  radius: 50
                  corners: ['top left', 'bottom left']
                  color: red
              - size: { width: 600, height: 400 }
                offset: { x: 375, y: 115 }
                rectangle:
                  radius: 200
                  corners: ['top right', 'bottom right']
                  color: green

    .. py:attribute:: border
        :type: Border

        The shape's outlining `border <Border>` specification.

    .. py:attribute:: color
        :type: str | None

        The shape's fill color.

        .. seealso:: Please review :ref:`choosing_a_color` section for more detail.
