Configuration
=============

To use this extension, it must be added to your conf.py file's :confval:`extensions` option.

.. code-block:: python
    :caption: Add this extension to your conf.py

    extension = [
        # other extensions...
        "sphinx_social_cards",
    ]

There are some required configuration values (and other optional values) that can be specified in
conf.py file as well. So, the `social_cards <Social_Cards>` option also needs to be added to conf.py.

.. autoclass:: sphinx_social_cards.validators.Social_Cards
    :members:
    :exclude-members: model_post_init

.. _choosing-a-font:

Choosing the font
-----------------

Fonts are fetched from Fontsource_ and cached in the `cache_dir` folder. They can be specified in
multiple places. The order of precedence is:

1. Using the `cards_layout_options.font <Cards_Layout_Options.font>` which is specified in the
   conf.py file under `social_cards.cards_layout_options <Social_Cards.cards_layout_options>` field.

   .. code-block:: python
       :caption: in conf.py

       social_cards = {
           "cards_layout_options": {
               "font": {
                   "family": "Roboto",
               }
           }
       }

2. The `typography.font <Typography.font>` attribute allows for finite control over each
   layer of text when using :doc:`layouts/index`.

   .. code-block:: yaml
       :caption: my-custom-layout.yml

       layers:
         - typography:
             font:
               family: "Roboto"

Both approaches use the same `font <Font>` specification.

.. note::
    The ``Roboto`` font is cached and distributed with this extension.

    If fonts cannot be fetched from Fontsource_ (and they are not already cached in the
    `cache_dir` or the distributed cache of ``Roboto`` fonts), then an error will be thrown.

Weights over styles
~~~~~~~~~~~~~~~~~~~

Fontsource_ does not offer ``bold`` or ``thin`` (AKA ``narrow``) styles of fonts. Instead they
offer a multitude of `weight`\ s. The rule of thumb is to to use

- :yaml:`100` instead of ``thin``
- :yaml:`400` instead of ``regular``
- :yaml:`700` instead of ``bold``

Fonts from Fontsource_ typically have only ``normal`` or ``italic`` `style`\ s. The `weight`\ s
available vary per font `family`. When a specified font does not provide the specified `weight`,
then the closest available weight is used.


.. warning::
    :title: Variable and icon fonts are not supported
    :collapsible:

    Since this extension uses ``pillow`` to render fonts, the support for using ``pillow`` with variable
    fonts has not been implemented. This is because ``pillow`` requires additional dependencies to
    work with variable fonts.

    Icon fonts, namely the material icon fonts from Google via Fontsource_, are also no supported
    because they are designed to be used in a browser with CSS capability. Implementing icon fonts
    without CSS, would require using special string syntax in the yaml layout, and it just
    doesn't seem worth it.

    If someone is so inclined to add support for variable and icon fonts, then a `Pull Request
    <https://github.com/2bndy5/sphinx-social-cards>`_ would be welcome.

Non-English languages
~~~~~~~~~~~~~~~~~~~~~~

Some fonts will render boxes because they do not contain CJK characters, like for example the
default `font <Font>`, ``Roboto``. If any text (eg. the :confval:`project` name,
:meta-field:`description`, or page :meta-field:`title`) contain CJK characters, then choose another
font from `Fontsource`_ which comes with CJK characters.

.. jinja::

    .. md-tab-set::

        {% set examples = {"TC": "Chinese (Traditional)", "SC": "Chinese (Simplified)", "JP": "Japanese", "KR": "Korean"} %}
        {% for variant, name in examples.items() %}
        {% set subset = name | replace('(', '') | replace(')', '') | lower | replace(' ', '-') %}

        .. md-tab-item:: {{name}}

            .. code-block:: python
                :caption: Using the the Noto Sans font family's ``{{ subset }}`` subset

                social_cards = {
                    "cards_layout_options": {
                        "font": {
                            "family": "Noto Sans {{variant}}",
                            "subsets": "{{ subset }}",
                        }
                    }
                }

        {% endfor %}

.. _metadata-fields:

Metadata
--------

Changing the title
~~~~~~~~~~~~~~~~~~

By default all generated social cards' title will use the page's top-level heading, but it may be
desirable to adapt the title to the page for which the social card represents. To do this,
use one of the following options:

- .. meta-field:: title

      A metadata field at the top of the document's source.

      .. code-block:: rst

          :title: Some page-specific title

- the :du-dir:`title directive <metadata-document-title>`

  .. code-block:: rst

      .. title:: Some page-specific title

- the :du-dir:`meta directive <metadata>`

  .. admonition::

      This option is more advanced as it allows direct manipulation of the resulting
      :du-tree:`meta element(s) <meta>`. However, this tactic will ensure the metadata is
      present in the generated HTML despite whatever theme is used.

  .. code-block:: rst

      .. meta::
        :title: Some page-specific title

Changing the description
~~~~~~~~~~~~~~~~~~~~~~~~

By default all generated social cards' description will use the `description <Social_Cards.description>`,
but it may be desirable to adapt the description to the page for which the social card represents.
To do this, use one of the following options:

- .. meta-field:: description

      A metadata field at the top of the document's source.

      .. code-block:: rst

          :description: Some page-specific description.

- the :du-dir:`meta directive <metadata>`

  .. admonition::

      This option is more advanced as it allows direct manipulation of the resulting
      :du-tree:`meta element(s) <meta>`. However, this tactic will ensure the metadata is
      present in the generated HTML despite whatever theme is used.

  .. code-block:: rst

      .. meta::
        :description: Some page-specific description.

Changing the icon
~~~~~~~~~~~~~~~~~

By default all generated social cards' icon will use the `Cards_Layout_Options.logo`,
but it may be desirable to adapt the icon to the page for which the social card represents.

.. note::
    :title: Changing the icon may not be consistent for different layouts.

    Some layouts use the icon differently from the :confval:`html_logo` (or
    :themeconf:`icon`\ [:themeconf:`logo`] for the sphinx-immaterial_ theme).

    When a layout uses an :meta-field:`icon` is used instead of the `logo
    <Cards_Layout_Options.logo>` (as with the ``default`` layout), then the color of the icon
    is not altered.

To do this, use either the :meta-field:`icon` or the :meta-field:`card-icon` metadata field.

.. meta-field:: icon

    A way to override the icon used in a certain pages social card. The file specified is relative
    to a path declared in the `image_paths <Social_Cards.image_paths>` list. If a file extension is not
    given, then ``.svg`` is assumed.

    .. code-block:: rst

        :icon: material/alert-decagram

.. meta-field:: card-icon

    If the used sphinx theme already has assigned behavior to an :meta-field:`icon`, then the
    :meta-field:`card-icon` can be used instead. It behaves the same for the purpose of this
    sphinx-social-cards extension.

    .. code-block:: rst

        :card-icon: sphinx_logo.svg

Blog front matter
~~~~~~~~~~~~~~~~~

Some of the front matter supported by the `ABlog sphinx extension
<https://ablog.readthedocs.io/en/stable/#how-it-works>`_ is used in the the pre-defined ``blog``
`cards_layout`:

.. meta-field:: tags

    This can be used as a comma-separated list of tags.

    .. code-block:: rst

        :tags: sphinx, social, cards

.. meta-field:: date

    This can be used as a hard-coded date instead of using ``config.today`` in the
    `jinja contexts <jinja-ctx>`.

    .. code-block:: rst

        :date: June 3 2023

    .. example:: Setting the date dynamically
        :collapsible:

        On Linux/MacOS, you can add a ``-`` between the ``%`` and format character to strip a
        leading zeroes. On windows, you would use a ``#`` instead of a ``-``.

        .. literalinclude:: conf.py
            :language: python
            :caption: conf.py
            :start-after: # BEGIN manually setting date
            :end-before: # END manually setting date

.. meta-field:: language

    This can be used as a spelled out language name instead of using ``config.language`` in the
    `jinja contexts <jinja-ctx>`.

    .. code-block:: rst

        :language: English

.. meta-field:: author

    This can be used as a specific author name instead of using ``config.author`` in the
    `jinja contexts <jinja-ctx>`.

    .. code-block:: rst

        :author: Brendan Doherty

Debugging Layouts
-----------------

.. autoclass:: sphinx_social_cards.validators.Debug
    :members:
