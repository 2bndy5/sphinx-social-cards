Basic Shapes
============

There are a few basic shapes supported. These shapes all use a common attribute called
`border <Border>` to control rendering the stroke that outlines the shapes.

.. py:class:: Border

    .. py:attribute:: width
        :type: int
        :value: 1

        The border's width in pixels. Defaults to :yaml:`0`.

    .. py:attribute:: color
        :type: str | None

        The border's color.

        .. seealso:: Please review :ref:`choosing_a_color` section for more detail.

.. toctree::
    :maxdepth: 1

    ellipse
    rectangle
    polygon
