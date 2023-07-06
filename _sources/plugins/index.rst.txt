Plugins
=======

It is possible to make plugins for this ``sphinx_social_cards`` extension. Such plugins can

- create optional :ref:`Jinja contexts <jinja-ctx>` to use in generating social card images
- add layouts to the already available :ref:`pre-designed layouts <pre-designed-layouts>`
- add images for use in layouts

Creating a Plugin
-----------------

A typical plugin involves a ``setup()`` function and another function that gets called when Sphinx
has prepared the builder for use (the :sphinx-event:`builder-inited`). For more details on writing
a sphinx extension, see the `Sphinx Hello World tutorial
<https://www.sphinx-doc.org/en/master/development/tutorials/helloworld.html>`_.

.. code-block:: python

    from sphinx.application import Sphinx

    def on_builder_init(app: Sphinx):
        # add contexts, layouts, or images from here
        pass

    def setup(app: Sphinx):
        # connect your on_builder_init() to the builder-inited event
        app.connect("builder-inited", on_builder_init)

.. _cookiecutter: https://cookiecutter.readthedocs.io/en/stable/

.. success:: Cookiecutter Available

    This extension is hosted on github with a cookiecutter_ template that can be used to
    quickly make a plugin that is ready for deployment. Just clone the repository then run the
    cookiecutter_ module on the cloned repository's "cookiecutter" directory.

    .. code-block:: shell

        git clone https://github.com/2bndy5/sphinx-social-cards
        pip install cookiecutter
        cookiecutter sphinx-social-cards/cookiecutter

    Follow the prompts and it will generate a new python project in the working directory.

Adding Context
**************

First, write a typical sphinx extension that hooks into the :sphinx-event:`builder-inited`. See
`Creating a Plugin`_. Then, add a `dict` of context information to the build environment using
`add_jinja_context()`.

.. warning::
    Please *do not* use hyphenated names in the `dict`\ 's keys as it would cause a Jinja parsing
    error if not using the `dict` notation. It is recommended to use snake casing in the key names
    for user convenience.

    .. md-tab-set::

        .. md-tab-item:: Using hyphens in key names

            .. code-block:: jinja

                {{ plugin['my-ctx'].example }}

        .. md-tab-item:: Not using hyphens in key names

            .. code-block:: jinja

                {{ plugin.my_ctx.example }}

.. code-block:: python

    from sphinx.application import Sphinx
    from sphinx_social_cards.plugins import add_jinja_context

    def on_builder_init(app: Sphinx):
        my_ctx = {"example": "hello world"}
        add_jinja_context(app, {"my_ctx": my_ctx})

Done! Now the added context is available in the `plugin <JinjaContexts.plugin>` context:

.. code-block:: yaml

    layers:
      - typography:
          content: '{{ plugin.my_ctx.example }}'

Adding Layouts
**************

First, write a typical sphinx extension that hooks into the :sphinx-event:`builder-inited`. See
`Creating a Plugin`_. Then, add the directory of layouts from the plugin to the
`cards_layout_dir` `list` using `add_layouts_dir()`. The path added *must* be an **absolute path**.

.. warning::
    **Do not** use the same names as the :ref:`pre-designed layouts <pre-designed-layouts>`.
    If a ``default`` layout exists in the plugin's layouts path, then it will override the original
    ``default`` layout.

    Instead, you should namespace your plugin's layouts with a subdirectory name. For example, a
    ``bitbucket`` plugin can have layouts in the plugin's ``layouts/bitbucket`` directory. When the
    layouts are added, the layout ``bitbucket/default`` will not override the ``default`` layout.

.. code-block:: python

    from pathlib import Path
    from sphinx.application import Sphinx
    from sphinx_social_cards.plugins import add_layouts_dir

    def on_builder_init(app: Sphinx):
        add_layouts_dir(app, Path(__file__).parent / "layouts")

Done! Now the search for a specified layout will include the plugin's directory of layouts.

Adding Images
*************

First, write a typical sphinx extension that hooks into the :sphinx-event:`builder-inited`. See
`Creating a Plugin`_. Then, add the directory of images from the plugin to the
`image_paths` `list` using `add_images_dir()`. The path added *must* be an **absolute path**.

.. warning::
    Do take care of the image names as they can take precedence over another image using the same
    name from a different path.

    Instead, you should namespace your plugin's images with a subdirectory name. For example, a
    ``bootstrap`` plugin can have images in the plugin's ``images/bootstrap`` folder. When the images
    are added, the image ``bootstrap/logo.png`` will not take precedence over another image named
    ``logo.png``.

.. code-block:: python

    from pathlib import Path
    from sphinx.application import Sphinx
    from sphinx_social_cards.plugins import add_images_dir

    def on_builder_init(app: Sphinx):
        add_images_dir(app, Path(__file__).parent / "images")

Done! Now the search for a specified image will include the plugin's directory of images.

API Reference
-------------

.. automodule:: sphinx_social_cards.plugins
    :members:
