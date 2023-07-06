Directives
==========

This extension comes with directives that can be used to generate an image for a social card
within a document's source file. The primary directive is the :rst:dir:`social-card` directive.
The :rst:dir:`image-generator` directive is a derivative to inject generated images into the document.

.. |dir-content| replace:: The content block (if provided) serves as a
    :doc:`custom layout <layouts/index>` written in YAML syntax.

.. rst:directive:: social-card

    This directive generates an image to use for a social card.

    :Argument:
        The optional argument (written in JSON syntax) can be used to override the configuration
        options set with `social_cards <Social_Cards>`. If no argument is provided, then the value
        from `social_cards <Social_Cards>` is used by default. Both the `social_cards
        <Social_Cards>` value and the argument provided are merged into a localized configuration.

        An example of passing the layout as an argument:

        .. rst-example::

            .. social-card::
                {
                    "cards_layout": "default/variant",
                    "cards_layout_options": {
                        "background_color": "orange"
                    }
                }
                :dry-run:

    :Content:
        |dir-content| If no content block is provided, then the
        `cards_layout <Social_Cards.cards_layout>` value is used.

        An example of passing the layout as a content block:

        .. rst-example::

            .. social-card::
                :dry-run:

                size: { width: 400, height: 200 }
                layers:
                  - ellipse:
                      color: green
                      border: { width: 15, color: light-blue }
                  - typography: { content: SSC, align: center, color: red }
                    size: { width: 350, height: 150 }
                    offset: { x: 25, y: 25 }

    .. warning::
        :name: non-op-dir-opts
        :title: Useless Options (demonstration purposes only)

        All options listed below are not meant for production use. They are intended for
        generating example images and injecting them into the document (without altering
        the page's metadata or the `social_cards <Social_Cards>` configuration).

        If you plan to use this directive to inject images into the document, then consider using
        the :rst:dir:`image-generator` directive instead. However, metadata and configuration cannot be
        manipulated using the :rst:dir:`image-generator` directive.

    .. rst:directive:option:: meta-data
        :type: JSON

        An optional string of :ref:`metadata-fields` written in JSON syntax.

        .. code-block:: rst
            :caption: Don't forget to indent a multi-lined value:

            .. social-card::
                :dry-run:
                :meta-data:
                    {
                        "title": "My overridden page title",
                        "icon": "images/messages.png"
                    }
                :hide-meta-data:

    .. rst:directive:option:: dry-run
        :type: flag

        This flag (if specified) will prevent the generated image from being used as the resulting
        document's social card. No metadata will be injected in the rendered document if this
        option is specified.

    .. rst:directive:option:: hide-meta-data
        :type: flag

        This flag (if specified) will hide the generated literal block displaying the given
        :rst:`:meta-data:`. If no :rst:`:meta-data:` is provided or the :rst:`:dry-run:` option is
        not used, then this flag is automatically asserted.

    .. rst:directive:option:: hide-conf
        :type: flag

        This flag (if specified) will hide the generated literal block displaying the configuration
        (given as an argument). If no configuration (directive argument) is provided or the
        :rst:`:dry-run:` option is not used, then this flag is automatically asserted.

    .. rst:directive:option:: hide-layout
        :type: flag

        This flag (if specified) will hide the generated literal block displaying the given layout
        (given as a content block). If no layout (directive content) is provided or the
        :rst:`:dry-run:` option is not used, then this flag is automatically asserted.

    .. rst:directive:option:: meta-data-caption
        :type: text

        This option will change the caption for the generated literal block displaying the given
        :rst:`:meta-data:`. Defaults to ``my-document.rst (meta-data)``.

    .. rst:directive:option:: conf-caption
        :type: text

        This option will change the caption for the generated literal block displaying the
        configuration (given as an argument). Defaults to ``conf.py``.

    .. rst:directive:option:: layout-caption
        :type: text

        This option will change the caption for the generated literal block displaying the given
        layout (given as a content block).  Defaults to ``my-layout.yml``.

.. rst:directive:: image-generator

    A simple directive designed to mimic the :du-dir:`image`, but the image is generated using
    this extension's mechanisms. If no content or argument is given, then the `cards_layout
    <Social_Cards.cards_layout>` value is used.

    .. important::
        Compared to the :rst:dir:`social-card` directive, this directive creates images that are
        *not* meant to be used as social media cards. Rather, it just creates an image and adds it
        to the document.

    .. seealso::
        Review the options to the :du-dir:`image` as the options are all the same. If no
        :rst:`:target:` option was given, then the image's URI is used as a target.

    :Argument:
        The only optional argument that this directive accepts is the layout name as given to the
        `cards_layout <Social_Cards.cards_layout>`.

        An example of passing the layout as an argument:

        .. rst-example::

            .. image-generator:: default/variant
                :align: center
    :Content:
        |dir-content|

        An example of passing the layout as a content block:

        .. rst-example::

            .. image-generator::
                :align: center

                size: { width: 400, height: 200 }
                layers:
                  - rectangle:
                      radius: 50
                      color: green
                      border: { width: 15, color: light-blue }
                  - typography: { content: SSC, align: center, color: red }
                    size: { width: 350, height: 150 }
                    offset: { x: 25, y: 25 }
