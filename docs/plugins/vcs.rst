``sphinx_social_cards.plugins.vcs``
===================================

.. automodule:: sphinx_social_cards.plugins.vcs
    :members:
    :exclude-members: CardGeneratorDirective

Added Layouts
-------------

These are examples of the layouts added:

.. jinja:: plugins.vcs

    {% for name, layouts in brands.items() %}

    {{ name }}
    {% for _ in name -%}*{%- endfor %}

    .. md-tab-set::

    {% for layout in layouts %}
        .. md-tab-item:: {{ layout }}

            .. image-generator:: {{ layout }}
    {% endfor %}
    {% endfor %}

Added Context
-------------

.. |protocol-stripped| replace:: (with protocols like ``https://`` stripped).
.. |added-ctx| replace:: A `dict` that can be accessed via

This plugin adds the following members to the ``plugin.*`` :ref:`jinja context <jinja-ctx>`:

GitHub Context
**************

.. autoclass:: sphinx_social_cards.plugins.vcs.utils.github.Github
    :members:

``repo`` Sub-Context
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: sphinx_social_cards.plugins.vcs.utils.github.Repo
    :members:

``owner`` Sub-Context
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: sphinx_social_cards.plugins.vcs.utils.github.Owner
    :members:

    .. autoattribute:: sphinx_social_cards.plugins.vcs.utils.github.Owner.login
    .. autoattribute:: sphinx_social_cards.plugins.vcs.utils.github.Owner.avatar

User List Sub-Contexts
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: sphinx_social_cards.plugins.vcs.utils.github.Contributor
    :members: login, avatar, contributions

.. autoclass:: sphinx_social_cards.plugins.vcs.utils.github.Organization
    :members: login, avatar, description
