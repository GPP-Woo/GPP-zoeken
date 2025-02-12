from datetime import date, datetime
from typing import TypedDict


class PublisherType(TypedDict):
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
