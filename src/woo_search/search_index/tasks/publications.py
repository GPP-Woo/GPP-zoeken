from datetime import date, datetime
from typing import List

from elasticsearch import NotFoundError

from woo_search.celery import app
from woo_search.utils.date import date_to_datetime

from ..client import get_client
from ..documents import Document, Publication
from ..typing import InformatieCategorieType, PublisherType


class DocumentNotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class PublicationNotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


@app.task()
def index_document(
    uuid: str,
    publicatie: str,
    publisher: PublisherType,
    identifier: str,
    officiele_titel: str,
    verkorte_titel: str,
    omschrijving: str,
    creatiedatum: date,
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
        creatiedatum=date_to_datetime(creatiedatum),
        registratiedatum=registratiedatum,
        laatst_gewijzigd_datum=laatst_gewijzigd_datum,
    )

    with get_client() as client:
        document.save(using=client)


@app.task()
def index_publication(
    uuid: str,
    publisher: PublisherType,
    informatie_categorieen: List[InformatieCategorieType],
    officiele_titel: str,
    verkorte_titel: str,
    omschrijving: str,
    registratiedatum: datetime,
    laatst_gewijzigd_datum: datetime,
):
    publication = Publication(
        _id=uuid,
        uuid=uuid,
        publisher=publisher,
        informatie_categorieen=informatie_categorieen,
        officiele_titel=officiele_titel,
        verkorte_titel=verkorte_titel,
        omschrijving=omschrijving,
        registratiedatum=registratiedatum,
        laatst_gewijzigd_datum=laatst_gewijzigd_datum,
    )

    with get_client() as client:
        publication.save(using=client)


@app.task()
def delete_document_index(uuid: str):
    with get_client() as client:
        try:
            document = Document.get(
                using=client,
                id=uuid,
            )
        except NotFoundError as err:
            raise DocumentNotFoundError(
                "Document with id {uuid} not found.".format(uuid=uuid)
            ) from err

        assert document
        document.delete(using=client)


@app.task()
def delete_publication_index(uuid: str):
    with get_client() as client:
        try:
            publication = Publication.get(
                using=client,
                id=uuid,
            )
        except NotFoundError as err:
            raise PublicationNotFoundError(
                "Publication with id {uuid} not found.".format(uuid=uuid)
            ) from err

        assert publication
        publication.delete(using=client)
