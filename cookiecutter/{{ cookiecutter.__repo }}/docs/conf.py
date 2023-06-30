# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "{{ cookiecutter.__repo }}"
copyright = "2023, {{ cookiecutter.author_name }}"
author = "{{ cookiecutter.author_name }}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx_social_cards", "{{ cookiecutter.package_name }}"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
# html_static_path = ["_static"]

# -- Options for sphinx_social_cards ------------------------------------------
# https://2bndy5.github.io/sphinx-social-cards/config.html
social_cards = {
    "description": "{{ cookiecutter.short_description }}",
    "site_url": "https://{{ cookiecutter.github_account }}.github.io/{{ cookiecutter.__repo }}",
}
