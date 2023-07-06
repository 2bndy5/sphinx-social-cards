from typing import Dict, cast, Tuple, Type, Optional

import sphinx
from sphinx.builders.html import StandaloneHTMLBuilder
import docutils.nodes
from .validators import Social_Cards


meta_node_types: Tuple[Type[docutils.nodes.Element], ...]

if sphinx.version_info >= (6,):
    meta_node_types = (docutils.nodes.meta,)  # type: ignore[attr-defined]
else:
    from sphinx.addnodes import (  # type: ignore[attr-defined]
        docutils_meta,
        meta as sphinx_meta,
    )

    meta_node_types = (docutils_meta, sphinx_meta)


def complete_doc_meta_data(
    existing_meta_data: Dict[str, str],
    builder: StandaloneHTMLBuilder,
    title: str,
    description: str,
    card_config: Social_Cards,
    page_name: str,
    img_hash: str,
) -> Tuple[Optional[str], Dict[str, str]]:
    new_meta_data: Dict[str, str] = {}
    if not isinstance(builder, StandaloneHTMLBuilder):
        return (None, new_meta_data)  # nothing left to do then
    uri = builder.get_target_uri(page_name)
    site_url = card_config.site_url.rstrip("/")
    page_url = "/".join([site_url, uri])
    uri = uri.rstrip(builder.link_suffix) + f"-{img_hash}.png"
    img_url = "/".join([site_url, card_config.path, uri])

    def update_meta(id_: Dict[str, str], content: str):
        prop, type_ = id_.popitem()
        attr_name = f"{prop}={type_}"
        # check if meta_data already exists
        if type_ not in existing_meta_data or attr_name not in existing_meta_data:
            # LOGGER.info("adding <meta %s content=%s/>", attr_name, content)
            # setdefault() used to exclude duplicates
            new_meta_data.setdefault(attr_name, content)

    update_meta(id_={"name": "twitter:card"}, content="summary_large_image")
    update_meta(id_={"property": "og:type"}, content="website")
    update_meta(id_={"property": "og:url"}, content=page_url)
    for key, val in dict(
        type="image/png",
        width=card_config._parsed_layout.size.width,
        height=card_config._parsed_layout.size.height,
    ).items():
        update_meta(id_={"property": f"og:{key}"}, content=str(val))
    for key, val in dict(title=title, description=description, image=img_url).items():
        assert val is not None, f"{key} cannot be None"
        update_meta(id_={"property": f"og:{key}"}, content=val)
        update_meta(id_={"name": f"twitter:{key}"}, content=val)
    if "title" not in existing_meta_data:
        new_meta_data.setdefault("title", title)
    if "description" not in existing_meta_data:
        new_meta_data.setdefault("description", description)

    return (uri, new_meta_data)


def add_doc_meta_data(document: docutils.nodes.document, meta_data: Dict[str, str]):
    parent = docutils.nodes.Element()

    for key, val in meta_data.items():
        node = meta_node_types[0]()  # type: ignore[attr-defined]
        if "=" in key:
            k, v = key.split("=", 1)
            node[k] = v
            node["content"] = val
        else:
            node[key] = val
        parent += node

    # insert at begin of document
    index = (
        document.first_child_not_matching_class(
            (docutils.nodes.Titular, *meta_node_types)  # type: ignore[attr-defined]
        )
        or 0
    )
    document[index:index] = parent.children


def get_doc_meta_data(document: docutils.nodes.document) -> Dict[str, str]:
    ret_val = {}

    # extract meta_data fields from current doc (up until current line)
    doc_node_index = document.first_child_not_matching_class(
        docutils.nodes.PreBibliographic
    )
    if doc_node_index is not None:
        for node in cast(docutils.nodes.Element, document[doc_node_index]):
            if isinstance(node, docutils.nodes.field):
                # print("docutils meta_data:", node)
                assert len(node) == 2
                field_name = cast(docutils.nodes.field_name, node[0]).astext()
                field_body = cast(docutils.nodes.field_body, node[1]).astext()
                if field_body:
                    ret_val.update({field_name: field_body})

    # extract meta_data from meta directives in current doc (up until current line)
    meta_tags = [
        doc_node
        for doc_node in document.children
        if isinstance(doc_node, meta_node_types)
    ]
    for tag in meta_tags:
        assert isinstance(tag, docutils.nodes.Element)
        attrs = tag.attributes.copy()

        if "content" in attrs:
            value = attrs.pop("content")
            if "name" in attrs and attrs["name"] in ("title", "description"):
                ret_val.update({attrs["name"]: value})
            else:
                key = " ".join([f"{k}={v}" for k, v in attrs.items() if v])
                if key:
                    ret_val.update({key: value})

    return ret_val


def get_default_page_title(document: docutils.nodes.document):
    # docutils title directive adds a title attr to the document obj
    if "title" in document.attributes:
        return document["title"]
    index = document.first_child_matching_class(docutils.nodes.section)
    if index is None:
        return None
    section_node = cast(docutils.nodes.Element, document[index])
    assert isinstance(section_node[0], docutils.nodes.title)
    return section_node[0].astext()
