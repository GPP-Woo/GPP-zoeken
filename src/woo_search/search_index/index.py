from datetime import date, datetime
from typing import TYPE_CHECKING, List

from elasticsearch_dsl import (
    Date,
    Document as ES_Document,
    InnerDoc,
    Keyword,
    M,
    Mapping,
    Nested,
    Object,
    Text,
    mapped_field,
)

from .typing import IndexName, InformatieCategorieType, PublisherType


class Attachment(InnerDoc):
    content: M[str] = mapped_field(Text(analyzer="dutch"))


class Publisher(InnerDoc):
    uuid: M[str] = mapped_field(Text(required=True, fields={"keyword": Keyword()}))
    naam: M[str] = mapped_field(Text(required=True, fields={"keyword": Keyword()}))


class InformatieCategorie(InnerDoc):
    uuid: M[str] = mapped_field(Text(required=True, fields={"keyword": Keyword()}))
    naam: M[str] = mapped_field(Text(required=True, fields={"keyword": Keyword()}))


# create empty base mapping instance
DOCUMENT_MAPPING = Mapping()
# add the attachment to the mapping without adding it to the `Document` class.
DOCUMENT_MAPPING.field("attachment", Object(Attachment)._mapping.to_dict())


class Document(ES_Document):
    # See https://elasticsearch-dsl.readthedocs.io/en/latest/persistence.html#python-type-hints
    # for typing support.
    uuid: M[str] = mapped_field(Text(required=True))
    publicatie: M[str] = mapped_field(Text(required=True))
    informatie_categorieen: M[List[InformatieCategorieType]] = mapped_field(
        Nested(InformatieCategorie, required=True)
    )
    publisher: M[PublisherType] = mapped_field(Object(Publisher, required=True))
    identifier: M[str] = mapped_field(Text(analyzer="dutch", required=True))
    officiele_titel: M[str] = mapped_field(Text(analyzer="dutch", required=True))
    verkorte_titel: M[str] = mapped_field(Text(analyzer="dutch"))
    omschrijving: M[str] = mapped_field(Text(analyzer="dutch"))
    # ES stores everything internally as a datetime, but always returns a string when
    # reading it. elasticsearch-dsl then takes care of parsing this string into a date
    # instance rather than datetime. Note that ES will assume UTC for this, but the
    # time part is not relevant and the date values are naive (and assumed to be in the
    # Amsterdam timezone).
    creatiedatum: M[date] = mapped_field(Date(required=True, format="yyyy-MM-dd"))
    registratiedatum: M[datetime] = mapped_field(Date(required=True))
    laatst_gewijzigd_datum: M[datetime] = mapped_field(Date(required=True))

    if TYPE_CHECKING:
        # help the type checkers a little bit
        _id: str

    class Meta:
        mapping = DOCUMENT_MAPPING

    class Index:
        name: IndexName = "document"


class Publication(ES_Document):
    uuid: M[str] = mapped_field(Text(required=True))
    publisher: M[PublisherType] = mapped_field(Object(Publisher, required=True))
    informatie_categorieen: M[List[InformatieCategorieType]] = mapped_field(
        Nested(InformatieCategorie, required=True)
    )
    officiele_titel: M[str] = mapped_field((Text(analyzer="dutch", required=True)))
    verkorte_titel: M[str] = mapped_field(Text(analyzer="dutch"))
    omschrijving: M[str] = mapped_field(Text(analyzer="dutch"))
    registratiedatum: M[datetime] = mapped_field(Date(required=True))
    laatst_gewijzigd_datum: M[datetime] = mapped_field(Date(required=True))

    if TYPE_CHECKING:
        # help the type checkers a little bit
        _id: str

    class Index:
        name: IndexName = "publication"
