import logging
from datetime import date, datetime

from django.conf import settings

from elasticsearch import NotFoundError

from woo_search.celery import app

from .client import get_client
from .documents import Document, Publication
from .typing import InformatieCategorieType, PublisherType

logger = logging.getLogger(__name__)


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
        creatiedatum=creatiedatum,
        registratiedatum=registratiedatum,
        laatst_gewijzigd_datum=laatst_gewijzigd_datum,
    )

    with get_client() as client:
        document.save(using=client, refresh=settings.SEARCH_INDEX["REFRESH"])


@app.task()
def remove_document_from_index(uuid: str) -> None:
    """
    If the document with specified ``uuid`` is present in the index, remove it.

    :arg uuid: The ID of the document in Elastic Search.
    """
    with get_client() as client:
        try:
            document = Document.get(using=client, id=uuid)
            assert document is not None
        except NotFoundError as exc:
            logger.info("Document with ID %s not found, aborting.", uuid, exc_info=exc)
            return
        else:
            document.delete(using=client)


@app.task()
def index_publication(
    uuid: str,
    publisher: PublisherType,
    informatie_categorieen: list[InformatieCategorieType],
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
        publication.save(using=client, refresh=settings.SEARCH_INDEX["REFRESH"])


@app.task()
def remove_publication_from_index(uuid: str) -> None:
    """
    If the publication with specified ``uuid`` is present in the index, remove it.

    :arg uuid: The ID of the document in Elastic Search.
    """
    with get_client() as client:
        try:
            publication = Publication.get(using=client, id=uuid)
            assert publication is not None
        except NotFoundError as exc:
            logger.info(
                "Publication with ID %s not found, aborting.", uuid, exc_info=exc
            )
            return
        else:
            publication.delete(using=client)
