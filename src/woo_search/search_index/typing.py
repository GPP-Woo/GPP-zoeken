from datetime import datetime
from typing import Optional, TypedDict


class Publisher(TypedDict):
    uuid: str
    naam: str


class DocumentType(TypedDict):
    uuid: str
    publicatie: str
    publisher: Publisher
    identifier: Optional[str]
    officiele_titel: str
    verkorte_titel: Optional[str]
    omschrijving: Optional[str]
    creatiedatum: datetime
    registratiedatum: datetime
    laatst_gewijzigd_datum: datetime
