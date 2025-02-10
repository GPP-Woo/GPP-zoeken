from datetime import datetime
from typing import TYPE_CHECKING

from elasticsearch_dsl import Date, Document as ES_Document, M, Text, mapped_field


class Document(ES_Document):
    # See https://elasticsearch-dsl.readthedocs.io/en/latest/persistence.html#python-type-hints
    # for typing support.
    uuid: M[str] = mapped_field(Text(required=True))
    publicatie: M[str] = mapped_field(Text(required=True))
    publisher: M[str] = mapped_field(Text(required=True))
    identifier: M[str | None] = mapped_field(Text())
    officiele_titel: M[str] = mapped_field(Text(required=True))
    verkorte_titel: M[str | None] = mapped_field(Text())
    omschrijving: M[str | None] = mapped_field(Text())
    creatiedatum: M[datetime] = mapped_field(Date(required=True))
    registratiedatum: M[datetime] = mapped_field(Date(required=True))
    laatst_gewijzigd_datum: M[datetime] = mapped_field(Date(required=True))

    if TYPE_CHECKING:
        # help the type checkers a little bit
        _id: str

    class Index:
        name = "document"
