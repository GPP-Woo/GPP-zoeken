from datetime import datetime
from typing import TYPE_CHECKING, List

from elasticsearch_dsl import (
    Date,
    Document as ES_Document,
    InnerDoc,
    M,
    Nested,
    Object,
    Text,
    mapped_field,
)

from ..typing import InformatieCategorieType, PublisherType


class Publisher(InnerDoc):
    uuid: M[str] = mapped_field(Text(required=True))
    naam: M[str] = mapped_field(Text(required=True))


class InformatieCategorie(InnerDoc):
    uuid: M[str] = mapped_field(Text(required=True))
    naam: M[str] = mapped_field(Text(required=True))


class Document(ES_Document):
    # See https://elasticsearch-dsl.readthedocs.io/en/latest/persistence.html#python-type-hints
    # for typing support.
    uuid: M[str] = mapped_field(Text(required=True))
    publicatie: M[str] = mapped_field(Text(required=True))
    publisher: M[PublisherType] = mapped_field(Object(Publisher, required=True))
    identifier: M[str] = mapped_field(Text(required=True))
    officiele_titel: M[str] = mapped_field(Text(required=True))
    verkorte_titel: M[str] = mapped_field(Text())
    omschrijving: M[str] = mapped_field(Text())
    creatiedatum: M[datetime] = mapped_field(Date(required=True))
    registratiedatum: M[datetime] = mapped_field(Date(required=True))
    laatst_gewijzigd_datum: M[datetime] = mapped_field(Date(required=True))

    if TYPE_CHECKING:
        # help the type checkers a little bit
        _id: str

    class Index:
        name = "document"


class Publication(ES_Document):
    uuid: M[str] = mapped_field(Text(required=True))
    publisher: M[PublisherType] = mapped_field(Object(Publisher, required=True))
    informatie_categorieen: M[List[InformatieCategorieType]] = mapped_field(
        Nested(InformatieCategorie, required=True)
    )
    officiele_titel: M[str] = mapped_field((Text(required=True)))
    verkorte_titel: M[str] = mapped_field(Text())
    omschrijving: M[str] = mapped_field(Text())
    registratiedatum: M[datetime] = mapped_field(Date(required=True))
    laatst_gewijzigd_datum: M[datetime] = mapped_field(Date(required=True))

    if TYPE_CHECKING:
        # help the type checkers a little bit
        _id: str

    class Index:
        name = "publication"
