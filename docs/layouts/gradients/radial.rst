Radial Gradients
================

.. autoclass:: sphinx_social_cards.validators.common.Radial_Gradient
    :members: center, radius, focal_point, focal_radius

    .. autoattribute:: preset

        .. social-card::
            :dry-run:

            layers:
              - background:
                  radial_gradient:
                    preset: 84
                    # or equivalently
                    preset: PhoenixStart
                    center: { x: 600, y: 315 }
                    radius: 600

    .. autoattribute:: colors

        .. |gradient_positions| replace:: `center` and `radius`

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

    .. autoattribute:: spread

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
