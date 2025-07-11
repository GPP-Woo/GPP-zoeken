from collections.abc import Collection
from datetime import date, datetime
from typing import Annotated, Literal, TypedDict
from uuid import UUID

type IndexName = Literal["publication", "document", "topic"]


class NestedPublisherType(TypedDict):
    uuid: str
    naam: str


class NestedInformationCategoryType(TypedDict):
    uuid: str
    naam: str


class NestedTopicType(TypedDict):
    uuid: str
    officiele_titel: str


class DocumentType(TypedDict):
    uuid: str
    publicatie: str
    informatie_categorieen: list[NestedInformationCategoryType]
    onderwerpen: list[NestedTopicType]
    publisher: NestedPublisherType
    identifiers: list[str]
    identifier: Annotated[str, DeprecationWarning("Obsoleted by identifiers")]
    officiele_titel: str
    verkorte_titel: str
    omschrijving: str
    creatiedatum: date
    registratiedatum: datetime
    laatst_gewijzigd_datum: datetime


class DocumentIndexType(DocumentType):
    download_url: str
    file_size: int | None


class PublicationType(TypedDict):
    uuid: str
    publisher: NestedPublisherType
    informatie_categorieen: list[NestedInformationCategoryType]
    onderwerpen: list[NestedTopicType]
    identifiers: list[str]
    officiele_titel: str
    verkorte_titel: str
    omschrijving: str
    registratiedatum: datetime
    laatst_gewijzigd_datum: datetime


class TopicType(TypedDict):
    uuid: str
    officiele_titel: str
    omschrijving: str
    registratiedatum: datetime
    laatst_gewijzigd_datum: datetime


class SearchParameters(TypedDict):
    query: str
    page: int
    page_size: int
    sort: Literal["relevance", "chronological"]
    result_types: list[IndexName]
    registratiedatum_vanaf: datetime | None
    registratiedatum_tot: datetime | None
    laatst_gewijzigd_datum_vanaf: datetime | None
    laatst_gewijzigd_datum_tot: datetime | None
    creatiedatum_vanaf: date | None
    creatiedatum_tot_en_met: date | None
    publishers: Collection[UUID]
    informatie_categorieen: Collection[UUID]
    onderwerpen: Collection[UUID]
