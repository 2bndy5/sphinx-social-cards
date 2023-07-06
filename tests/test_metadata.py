import pytest
from sphinx.testing.util import SphinxTestApp


@pytest.mark.parametrize(
    "title",
    [
        ".. title:: A test title",
        ":title: A test title",
        ".. meta::\n    :title: A test title",
    ],
    ids=["directive", "field", "explicit"],
)
def test_title(sphinx_make_app, title: str):
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="""html_theme = 'furo'""",
        files={
            "index.rst": f"""
{title}

Test Title
==========

.. image-generator::
"""
        },
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())


def test_meta_directive(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="""html_theme = 'furo'""",
        files={
            "index.rst": """
.. meta::
    :property=og\\:description: A test description
    :property=og\\:title: A test title
    :twitter\\:description: A test description
    :twitter\\:title: A test title

Test Title
==========

.. image-generator::
"""
        },
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())


@pytest.mark.xfail
def test_before_title(sphinx_make_app) -> None:
    app: SphinxTestApp = sphinx_make_app(
        extra_conf="""html_theme = 'furo'
social_cards["enable"] = False
""",
        files={
            "index.rst": """
.. image-generator::

Test Title
==========

"""
        },
    )

    app.build()
    assert not app._warning.getvalue()
    # print(app._status.getvalue())
