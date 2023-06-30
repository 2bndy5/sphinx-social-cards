"""
{{ cookiecutter.package_name }}
{% for _ in cookiecutter.project_name -%}={%- endfor %}

{{ cookiecutter.short_description }}
"""
{% if cookiecutter.add_layout == 'True' or cookiecutter.add_image == 'True' -%}
from pathlib import Path
{%- endif %}
from sphinx.application import Sphinx
{%- set using_api = False %}
{% if cookiecutter.add_layout == 'True' or cookiecutter.add_context == 'True' or cookiecutter.add_image == 'True' -%}
    {%- set using_api = True -%}
    {%- set api_members = [] -%}
    {%- if cookiecutter.add_layout == 'True' -%}
    {%- set api_members = api_members + ['add_layouts_dir'] -%}
    {%- endif -%}
    {%- if cookiecutter.add_context == 'True' -%}
    {%- set api_members = api_members + ['add_jinja_context'] -%}
    {%- endif -%}
    {%- if cookiecutter.add_image == 'True' -%}
    {%- set api_members = api_members + ['add_images_dir'] -%}
    {%- endif -%}

from sphinx_social_cards.plugins import {{ api_members | join(', ') }}
{%- endif %}


def on_builder_init(app: Sphinx):
    # The main driving logic of the plugin.
    {% if not using_api -%}
    pass
    {%- endif %}

    {% if cookiecutter.add_layout == 'True' -%}
    # add this pkg's layouts/ folder to the config `cards_layout_dir` list
    add_layouts_dir(Path(__file__).parent / "layouts")
    {%- endif %}

    {% if cookiecutter.add_context == 'True' -%}
    # add this pkg's special jinja context to the builder env list of `plugin` contexts
    add_jinja_context({"{{ cookiecutter.package_name }}": {"example": "hello world"}})
    {%- endif %}

    {% if cookiecutter.add_image == 'True' -%}
    # add this pkg's images/ folder to the config `image_paths` list
    add_images_dir(Path(__file__).parent / "images")
    {%- endif %}


def setup(app: Sphinx):

    # connect your on_builder_init() to the builder-inited event
    app.connect("builder-inited", on_builder_init)

    # use app.setup_extension() to enable sphinx-social-cards plugins or other sphinx
    # extensions. Mind the dependencies listed in the root requirements.txt file for
    # third-party dependencies (eg. from pypi via pip).
    #
    # app.setup_extension("extension_name")

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
