Layer of a Layout
*****************

Each layer can be specified in layout's YAML file as a YAML list under the ``layers`` property.

.. autoclass:: sphinx_social_cards.validators.layout.Layer
    :members:

Using Jinja Syntax within the Layout
------------------------------------

.. seealso::
    It is advised to read up on how to use `Jinja syntax`_.

Layouts are Jinja Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A layout file is basically a Jinja template. So, layers can be generated dynamically using `Jinja
syntax`_.

.. social-card::
    :dry-run:
    :layout-caption: Drawing 3 circles programmatically with Jinja

    #{% set diameter, width, height = (100, 600, 250) %}
    size:
      width: {{ width }}
      height: {{ height }}
    layers:
      - background: { color: '#0000007F' }
      #{% for i in range(3) %}
      - ellipse:
          color: '#{{ ('0' * i) + 'F' + ('0' * (2 - i)) }}'
        size:
          width: {{ diameter }}
          height: {{ diameter }}
        offset:
          x: {{ width / 6 * (i * 2 + 1) - (diameter / 2) }}
          y: {{ (height - diameter) / 2  }}
      #{% endfor %}

Inheriting Layouts
~~~~~~~~~~~~~~~~~~

Layouts can even inherit from other layouts! For more information on template inheritance, see
the `Jinja documentation
<https://jinja.palletsprojects.com/en/latest/templates/#template-inheritance>`_.
For example, the ``default`` layout is inherited by ``default/accent`` and ``default/inverted``
layouts. In those layouts, a Jinja block (:jinja:`{% block color_vals %}`) is used to override the
inherited color aliases.

.. jinja::

    .. md-tab-set::

        {% for layout in ['default', 'default/accent', 'default/inverted'] %}
        .. md-tab-item:: {{ layout }}

            .. literalinclude:: ../../src/sphinx_social_cards/layouts/{{ layout }}.yml
                :language: yaml
                {% if layout == 'default' -%}
                :end-at: {{ '{%' }} endblock %}
                {%- endif %}
        {% endfor %}

.. note::
    The Jinja :jinja:`{% extends layout-file %}` statement requires the layout file name to be in
    quotes. Additionally, if inheriting from a layout in a sub-directory of layouts, then use the
    relative path to the layout.

    .. code-block:: jinja
        :caption: Inheriting from ``default/variant`` layout

        {% extends "default/variant.yml" %}

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

Referencing Jinja Contexts
~~~~~~~~~~~~~~~~~~~~~~~~~~

Items of `Jinja contexts <jinja-ctx>` can be referenced in the layout as `Jinja variables
<https://jinja.palletsprojects.com/en/3.1.x/templates/#variables>`_:

.. code-block:: yaml
    :caption: Getting the page title from the page context.

    layers:
      - typography:
          content: '{{ page.title }}'

Jinja syntax uses ``{`` and ``}`` which have a reserved meaning in YAML syntax.
For this reason, it is important to surround single-line YAML strings with quotes
when the string value begins with `Jinja syntax`_. This way the syntax conventions
for jinja and YAML are simultaneously respected.

.. code-block:: yaml
    :caption: Surrounding quotes are not required for multi-line YAML strings.

    layers:
      - icon:
          image: >-
            {% if page.meta.icon %}
            {{ page.meta.icon }}
            {% else %}
            {{ layout.logo.image }}
            {% endif %}

.. hint::
    :title: Escaping Jinja References
    :collapsible:

    Use :jinja:`{{ '{{' }}` to escape a Jinja reference.

    .. code-block:: yaml

        layers:
          - typography:
              content: "{{ '{{' }} page.title }}"
              # renders as: "{{ page.title }}"
