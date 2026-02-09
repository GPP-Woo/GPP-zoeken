from collections.abc import Iterator

from elasticsearch.dsl import Document


def get_subclasses(cls: type):
    for subclass in cls.__subclasses__():
        yield from get_subclasses(subclass)
        yield subclass


def get_index_document_types() -> Iterator[type[Document]]:
    yield from get_subclasses(Document)
