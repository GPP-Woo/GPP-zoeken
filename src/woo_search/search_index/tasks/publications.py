from datetime import datetime

from woo_search.celery import app

from ..client import get_client
from ..documents import Document
from ..typing import Publisher


@app.task()
def index_document(
    uuid: str,
    publicatie: str,
    publisher: Publisher,
    identifier: str,
    officiele_titel: str,
    verkorte_titel: str,
    omschrijving: str,
    creatiedatum: datetime,
    registratiedatum: datetime,
    laatst_gewijzigd_datum: datetime,
):
    document = Document(
        _id=uuid,
        uuid=uuid,
        publicatie=publicatie,
        publisher=publisher,
        identifier=identifier,
        officiele_titel=officiele_titel,
        verkorte_titel=verkorte_titel,
        omschrijving=omschrijving,
        creatiedatum=creatiedatum,
        registratiedatum=registratiedatum,
        laatst_gewijzigd_datum=laatst_gewijzigd_datum,
    )

    with get_client() as client:
        document.save(using=client)
