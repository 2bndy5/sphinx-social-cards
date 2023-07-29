Layer of a Layout
=================

Each layer can be specified in layout's YAML file as a YAML list value for the ``layers`` mapping.

.. social-card::
    :dry-run:
    :layout-caption: A simple layout of 2 layers

    size: { width: 250, height: 250 }
    layers:  # each layer in this list is denoted with a dash ('-')
      - # layer 0
        background:
          color: orange
      - # layer 1
        icon:
          image: sphinx_logo

.. autoclass:: sphinx_social_cards.validators.layout.Layer
    :members:

.. _using_jinja:

Using Jinja Syntax within the Layout
------------------------------------

.. seealso::
    It is advised to read up on how to use |Jinja syntax|.

Conventionally, |Jinja syntax| uses characters that have actual meaning in YAML. To help
streamline the combination of YAML and Jinja syntaxes, this extension uses a modified jinja
syntax:

.. list-table:: differences between Jinja syntax
    :header-rows: 1
    :stub-columns: 1

    - *
      * Conventional
      * sphinx-social-cards
    - * :external+jinja_doc:ref:`line-statements`
      * :jinja:`{% ... %}`
      * :yaml:`#% ... %#`
    - * :external+jinja_doc:ref:`expressions`
      * ``{{ ... }}``
      * :yaml:`'{{ ... }}'` [1]_
    - * :external+jinja_doc:ref:`comments`
      * :jinja:`{# ... #}`
      * :yaml:`## ... ##`

.. [1] In the case of jinja expressions, the surrounding single quotes are removed by Jinja
    and are not passed on to the YAML parser. Meaning, :yaml:`'{{ ... }}'` appears to the
    YAML parser like so: ``...``

Escaping Jinja Syntax
~~~~~~~~~~~~~~~~~~~~~

Use :jinja:`'{{ "'{{" }}'` to escape a Jinja reference.

.. code-block:: yaml

    layers:
      - typography:
          content: "'{{ "'{{" }}' page.title }}"
          # renders as: "{{ page.title }}"

Layouts are Jinja Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A layout file is basically a Jinja template. So, layers can be generated dynamically using
|Jinja syntax|.

.. social-card::
    :dry-run:
    :layout-caption: Drawing 3 circles programmatically with Jinja

    #% set diameter, width, height = (100, 600, 250) %#
    size:
      width: '{{ width }}'
      height: '{{ height }}'
    layers:
      - background: { color: '#0000007F' }
      #% for i in range(3) %#
      - ellipse:
          color: "#'{{ ('0' * i) + 'F' + ('0' * (2 - i)) }}'"
        size:
          width: '{{ diameter }}'
          height: '{{ diameter }}'
        offset:
          x: '{{ width / 6 * (i * 2 + 1) - (diameter / 2) }}'
          y: '{{ (height - diameter) / 2  }}'
      #% endfor %#

Inheriting Layouts
~~~~~~~~~~~~~~~~~~

Layouts can even inherit from other layouts! The Jinja documentation has an excellent explanation
on :external+jinja_doc:ref:`template-inheritance`. The rest of this section builds upon that useful
information, so please read that first.

As a quick example, the ``default`` layout is inherited by ``default/accent`` and ``default/inverted``
layouts. In those layouts, a Jinja block (:jinja:`#% block color_vals %#`) is used to override the
inherited color aliases.

.. jinja::

    .. md-tab-set::

        {% for layout in ['default', 'default/accent', 'default/inverted'] %}
        .. md-tab-item:: {{ layout }}

            .. literalinclude:: ../../src/sphinx_social_cards/layouts/{{ layout }}.yml
                :language: yaml
                {% if layout == 'default' -%}
                :end-at: #% endblock %#
                {%- endif %}
        {% endfor %}

.. note::
    The Jinja :jinja:`#% extends layout-file %#` statement requires the layout file name to be in
    quotes. Additionally, if inheriting from a layout in a sub-directory of layouts, then use the
    relative path to the layout.

    .. code-block:: jinja
        :caption: Inheriting from ``default/variant`` layout

        #% extends "default/variant.yml" %#

Inheritance Tutorial
********************

Let's say you want to change the pre-designed ``opengraph`` layout into a dark themed version.
This can easily be done by inheriting the ``opengraph`` layout in your new custom layout. Upon
inspection, we will find 3 jinja blocks in the ``opengraph`` layout's source:

1. The ``font_colors`` block defines the colors used for fonts:

   .. literalinclude:: ../../src/sphinx_social_cards/layouts/opengraph.yml
       :language: yaml
       :caption: opengraph.yml
       :linenos:
       :lineno-match:
       :start-at: #% block font_colors %#
       :end-at: #% endblock %#

   .. important::
       We only need to change the actual color values.

       .. error:: Changing the repeated tag names will break the layout.
2. The ``background`` block defines the layer that specifies the background:

   .. literalinclude:: ../../src/sphinx_social_cards/layouts/opengraph.yml
       :language: yaml
       :caption: opengraph.yml
       :linenos:
       :lineno-match:
       :start-at: #% block background -%#
       :end-at: #%- endblock %#

3. The ``watermark_icon`` block defines the layer that specifies the sphinx logo in the bottom
   corner:

   .. literalinclude:: ../../src/sphinx_social_cards/layouts/opengraph.yml
       :language: yaml
       :caption: opengraph.yml
       :linenos:
       :lineno-match:
       :start-at: #% block watermark_icon -%#
       :end-at: #%- endblock %#

   .. note::
       We could of course change this image via the :meta-field:`cards-icon`. But, notice the color
       for the icon is hard-coded because the background color is also hard-coded.

.. question:: What about the other colors and stuff?

    The color and image of the logo is already optionally controlled via the
    `cards_layout_options`\ [`logo`]. Additionally, the color of the bottom stripe can already be
    controlled via the `cards_layout_options`\ [`accent`]. Any further changes would necessitate a
    completely new layout.

Now, we will create our custom layout file in the sphinx project's source folder (adjacent to the
conf.py file) - typically in a ``docs`` directory. Remember to add the directory path of this new
layout to `social_cards <Social_Cards>`\ [`cards_layout_dir`] and
`social_cards <Social_Cards>`\ [`cards_layout`] in the conf.py file. For this example, the new
layout will be located in ``docs/social_cards/opengraph-dark.yml``, so we add:

.. code-block:: python
    :caption: conf.py
    :emphasize-lines: 4, 5

    social_cards = {
        "site_url": html_base_url,
        "description": "a project-wide description",
        "cards_layout_dir": "social_cards",
        "cards_layout": "opengraph-dark",
    }

In the newly created ``opengraph-dark.yml`` file, we inherit the ``opengraph`` layout and make our
customizations:

.. social-card::
    :dry-run:
    :layout-caption: opengraph-dark.yml

    #% extends "opengraph.yml" %#
    #% block font_colors %#
    project_desc_color: &project_desc_color 'rgb(239, 240, 241)'
    title_url_color: &title_url_color 'rgb(222, 230, 237)'
    #% endblock %#

    # We need to keep the same indent as the inherited source,
    # otherwise the YAML parser may get confused.

      #% block background -%#
      - background:
          linear_gradient:
            start: {}
            end: { x: 400, y: 210}
            spread: reflect
            colors:
              0.0: rgb(23, 23, 23)
              0.35: rgb(18, 18, 18)
              1.0: rgb(13, 13, 13)
      #%- endblock %#

        #% block watermark_icon -%#
        icon:
          image: sphinx_logo
          color: rgb(116, 116, 83)
        #%- endblock %#

Referencing Jinja Contexts
~~~~~~~~~~~~~~~~~~~~~~~~~~

Items of `Jinja contexts <jinja-ctx>` can be referenced in the layout as
:external+jinja_doc:ref:`Jinja variables <variables>`:

.. code-block:: yaml
    :caption: Getting the page title from the page context.

    layers:
      - typography:
          content: '{{ page.title }}' # (1)!
          color: '{{ undefined }}' # (2)!

.. code-annotations::
    1. A YAML string that begins with a letter does not require extra surrounding quotes. Here,
       the single quotes are required for Jinja expressions, but they are removed by Jinja before
       the YAML is parsed.
    2. Any reference to an undefined `Jinja context variable <jinja-ctx>` is automatically
       converted to the YAML :yaml:`null` value. This can be useful for font colors because a
       :yaml:`null` value will fallback to using the value of `layout.color
       <Cards_Layout_Options.color>`.

.. code-block:: yaml
    :caption: Conditionally referencing context string values with a multi-line YAML string.

    layers:
      - icon:
          image: >- # (1)!
            #% if page.meta.icon %#
            '{{ page.meta.icon }}'
            #% else %#
            '{{ layout.logo.image }}'
            #% endif %#

.. code-annotations::
    1. Here ``>`` signifies that the following indented block is a single string, but line breaks
       are replaced with spaces. With ``-``, ``>-`` instructs the YAML parser to strip a trailing
       line break from the multi-line string.

The ``yaml`` Jinja filter (for referencing color values)
********************************************************

.. seealso::
    Jinja comes with a bunch of documented :external:ref:`builtin filters <builtin-filters>`.
    General usage is briefly described in the :external:ref:`Jinja Filters section <filters>`.

Not all `Jinja contexts <jinja-ctx>` hold a `str` or `int` value. For example, a color that was
specified as a gradient will be in the form of a Python `dict`. If you want to support color
gradients in the layout, then a custom filter (``yaml``) is added to the Jinja environment that
parses the layout before the YAML parser reads the layout.

.. code-block:: yaml
    :caption: Referencing a color value from jinja context

    layers:
      - background:
          color: '{{ layout.background_color | yaml }}' # (1)!

.. code-annotations::
    1. A `background_color <Cards_Layout_Options.background_color>` specified as a
       gradient like so:

       .. code-block:: python

           social_cards = {
               "cards_layout_options": {
                   "background_color": { # a linear gradient
                       "start": {"x": 0, "y": 0 },
                       "end": {"x": 1200, "y": 630},
                       "preset": 84,  # aka "PhoenixStart"
                   },
               },
           }

       will be converted to a proper YAML mapping with the ``yaml`` filter:

       .. code-block:: yaml

           color: { start: { x: 0, y: 0 }, end: { x: 1200, y: 630 }, preset: 84 }

.. note::
    :title: Solid colors do not need the ``yaml`` filter

    All `Jinja Contexts <jinja-ctx>` that define a :ref:`solid color <solid_color>` are
    automatically translated to use the string form, ``rgb(<red>, <green>, <blue>)`` (or
    ``rgba(<red>, <green>, <blue>, <alpha>)`` if an alpha value/transparency was included).

    Meaning, layout designers do not have to worry about colors specified with a beginning
    ``#`` which would be interpreted as a YAML comment (eg: :python:`"#0FF1CE"` is translated
    to :yaml:`rgb(15, 241, 206)`).

.. warning::
    Do not use a multi-line YAML string to reference colors from `Jinja contexts <jinja-ctx>`.
    Doing so will result in a quoted YAML value:

    .. code-block:: yaml
        :caption: Do not do this!

        layers:
          - background:
              color: >-
                #% if layout.logo.color %#
                '{{ layout.logo.color | yaml }}'
                #% else %#
                '{{ layout.background_color | yaml }}'

    .. code-block:: yaml
        :caption: Do this instead

        layers:
          - background:
              color: #% if layout.logo.color %#'{{ layout.logo.color | yaml }}'#% else %#'{{ layout.background_color | yaml }}'

.. _jinja-ctx:

Jinja Contexts
~~~~~~~~~~~~~~

Every generated social card uses a set of Jinja contexts:

.. autoclass:: sphinx_social_cards.validators.contexts.Config
  :members:
.. autoattribute:: sphinx_social_cards.validators.contexts.JinjaContexts.layout
.. autoclass:: sphinx_social_cards.validators.contexts.Page
  :members:
.. autoattribute:: sphinx_social_cards.validators.contexts.JinjaContexts.plugin
