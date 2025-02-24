from datetime import date, datetime
from typing import Literal, TypedDict

type IndexName = Literal["publication", "document"]


class PublisherType(TypedDict):
    uuid: str
    naam: str


class InformatieCategorieType(TypedDict):
    uuid: str
    naam: str


class DocumentType(TypedDict):
    uuid: str
    publicatie: str
    publisher: PublisherType
    identifier: str
    officiele_titel: str
    verkorte_titel: str
    omschrijving: str
    creatiedatum: date
    registratiedatum: datetime
    laatst_gewijzigd_datum: datetime


class PublicationType(TypedDict):
    uuid: str
    publisher: PublisherType
    informatie_categorieen: list[InformatieCategorieType]
    officiele_titel: str
    verkorte_titel: str
    omschrijving: str
    registratiedatum: datetime
    laatst_gewijzigd_datum: datetime


class SearchParameters(TypedDict):
    query: str
    page: int
    page_size: int
    sort: Literal["relevance", "chronological"]
    result_type: IndexName | Literal["*"]
    registratiedatum_vanaf: datetime | None
    registratiedatum_tot: datetime | None
    laatst_gewijzigd_datum_vanaf: datetime | None
    laatst_gewijzigd_datum_tot: datetime | None
    creatiedatum_vanaf: date | None
    creatiedatum_tot_en_met: date | None
