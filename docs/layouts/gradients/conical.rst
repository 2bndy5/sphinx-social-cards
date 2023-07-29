Conical Gradients
=================

.. autoclass:: sphinx_social_cards.validators.common.Conical_Gradient
    :members: center, angle

    .. autoattribute:: preset

        .. social-card::
            :dry-run:

            layers:
              - background:
                  conical_gradient:
                    preset: 84
                    # or equivalently
                    preset: PhoenixStart
                    center: { x: 600, y: 315 }
                    angle: 27.5

    .. autoattribute:: colors

        .. |gradient_positions| replace:: `center` and `angle`

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
