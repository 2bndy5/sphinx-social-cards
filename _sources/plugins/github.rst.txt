``sphinx_social_cards.plugins.github``
======================================

.. automodule:: sphinx_social_cards.plugins.github
    :members:

Added Layouts
-------------

These are examples of the layouts added:

.. jinja:: github_plugin_layouts

    {% if layouts -%}
    .. md-tab-set::
    {%- endif %}

    {% for layout in layouts %}
        .. md-tab-item:: {{ layout }}

            .. image-generator:: {{ layout }}
    {% endfor %}

Added Context
-------------

.. |protocol-stripped| replace:: (with protocols like ``https://`` stripped).
.. |added-ctx| replace:: A `dict` that can be accessed via

This plugin adds the following members to the ``plugin.*`` :ref:`jinja context <jinja-ctx>`:

.. autoclass:: sphinx_social_cards.plugins.github.context.Github
    :members:

``repo`` Sub-Context
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: sphinx_social_cards.plugins.github.context.Repo
    :members:

``owner`` Sub-Context
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: sphinx_social_cards.plugins.github.context.Owner
    :members:

    .. autoattribute:: sphinx_social_cards.plugins.github.context.Owner.login
    .. autoattribute:: sphinx_social_cards.plugins.github.context.Owner.avatar

User List Sub-Contexts
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: sphinx_social_cards.plugins.github.context.Contributor
    :members: login, avatar, contributions

.. autoclass:: sphinx_social_cards.plugins.github.context.Organization
    :members: login, avatar, description
