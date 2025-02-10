from collections.abc import Iterator

from elasticsearch_dsl import Document

from woo_search.utils.checks import get_subclasses


def get_index_document_types() -> Iterator[type[Document]]:
    for subcls in get_subclasses(Document):
        yield subcls
