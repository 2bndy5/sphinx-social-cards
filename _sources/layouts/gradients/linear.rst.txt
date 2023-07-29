Linear Gradients
================

.. autoclass:: sphinx_social_cards.validators.common.Linear_Gradient
    :members: start, end

    .. autoattribute:: preset

        .. social-card::
            :dry-run:

            layers:
              - background:
                  linear_gradient:
                    preset: 84
                    # or equivalently
                    preset: PhoenixStart
                    start: { x: 60, y: 60 }
                    end: { x: 1140, y: 570 }

    .. autoattribute:: colors

        .. |gradient_positions| replace:: `start` and `end`

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

    .. autoattribute:: spread

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
