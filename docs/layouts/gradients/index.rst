Gradient Colors
===============

.. warning::
    Gradient colors cannot be used for `debug <Debug>`\ [`color <Debug.color>`].

Detailed explanations and examples are shown for the supported types of gradients:

- :doc:`linear` require a `start <Linear_Gradient.start>` and
  `end <Linear_Gradient.end>` attributes.
- :doc:`radial` require a `center <Radial_Gradient.center>` and
  `radius <Radial_Gradient.radius>` attributes.
- :doc:`conical` require a `center <Conical_Gradient.center>` attribute while
  the necessary `angle <Conical_Gradient.angle>` attribute defaults to ``0``.

.. abstract:: Gradients are implemented as aliases of color
    :collapsible:

    Gradient specifications are implemented as aliased specification of the ``color``  attribute.
    So, one could specify a gradient using only the color attribute:

    .. code-block:: yaml
        :caption: specifying a ``linear_gradient`` using the ``color`` attribute

        color:
          start: { x: 50, y: 60 }
          end: { x: 150, y: 60 }
          preset: 48

    However, this isn't very readable. In the above example, there is very little to signify that
    we declared a linear gradient. This could also be confusing if a solid color is specified for a
    specific gradient:

    .. code-block:: yaml
        :caption: specifying a solid ``color`` using the ``linear_gradient`` attribute

        linear_gradient: white

    Nonetheless, either form will work as long as the specified value(s) is valid (regardless of
    the attribute name).

.. jinja::

    .. md-tab-set::

        .. md-tab-item:: in conf.py


            .. md-tab-set::

                {% for t in ['linear', 'radial', 'conical'] %}

                .. md-tab-item:: {{ t }} gradient

                    .. code-block:: python

                        social_cards = {
                            "cards_layout_options": {
                                "background_color": {
                                    "preset": "WideMatrix",  # (1)!
                                    {% if t == 'linear' -%}
                                    "start": { "x": 30, "y": 30 },
                                    "end": { "x": 1170, "y": 600 },
                                    {%- elif t == 'radial' -%}
                                    "center": { "x": 300, "y": 315 },
                                    "radius": 300,
                                    {%- elif t == 'conical' -%}
                                    "center": { "x": 600, "y": 315 },
                                    "angle": 45,
                                    {%- endif %}
                                },
                            },
                        }


                    .. code-annotations::
                        1. This uses one of the conveniently pre-defined :doc:`presets`.

                           .. seealso:: `{{ t }}_gradient.preset <{{ t | title }}_Gradient.preset>`
                {% endfor %}

        .. md-tab-item:: in a layout

            .. md-tab-set::

                {% for t in ['linear', 'radial', 'conical'] %}

                .. md-tab-item:: {{ t }} gradient

                    .. code-block:: yaml

                        layers:
                          - background:
                              {{ t }}_gradient:
                                preset: WideMatrix # (1)!
                                {% if t == 'linear' -%}
                                start: { x: 30, y: 30 }
                                end: { x: 1170, y: 600 }
                                {%- elif t == 'radial' -%}
                                center: { x: 300, y: 315 }
                                radius: 300
                                {%- elif t == 'conical' -%}
                                center: { x: 600, y: 315 }
                                angle: 45
                                {%- endif %}

                    .. code-annotations::
                        1. This uses one of the conveniently pre-defined :doc:`presets`.

                           .. seealso:: `{{ t }}_gradient.preset <{{ t | title }}_Gradient.preset>`
                {% endfor %}

.. toctree::
    :hidden:

    linear
    radial
    conical
    presets
