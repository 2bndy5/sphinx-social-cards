Layer Typography Attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: sphinx_social_cards.validators.layers.Typography
    :members:
    :exclude-members: border, model_fields, model_config

    .. autoattribute:: sphinx_social_cards.validators.layers.Typography.border

        .. seealso::
            This attribute shares the same `border <Border>` specification that is used by the
            supported :doc:`shapes/index`.
        .. important::
            If the `border.color <Border.color>` is not specified, then the
            `typography.color <Typography.color>` is used.

        .. social-card::
            :dry-run:
            :layout-caption: A stroke around transparent characters

            size: { width: 600, height: 110 }
            layers:
            - background: {color: "#4051b5"}
            - typography:
                content: Fancy Text
                color: '#00000000' # a transparent color
                align: center
                border:
                    width: 3
                    color: white

Typography Line specification
-----------------------------

.. autoclass:: sphinx_social_cards.validators.layers.Line
    :members:

Font specification
------------------

.. autoclass:: sphinx_social_cards.validators.layers.Font
    :members:
