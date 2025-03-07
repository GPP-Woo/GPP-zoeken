import base64
import logging
from datetime import date, datetime

from django.conf import settings

import requests
from elasticsearch import NotFoundError
from zgw_consumers.client import build_client
from zgw_consumers.models import Service

from woo_search.celery import app

from .client import get_client
from .constants import DOCUMENT_ATTACHMENT_PIPELINE_ID
from .index import Document, Publication
from .typing import InformatieCategorieType, PublisherType

logger = logging.getLogger(__name__)


def _download_document(document_url: str) -> str | None:
    if (service := Service.get_service(document_url)) is None:
        logger.exception("Couldn't find any matching GPP Publicatiebank Service.")
        return

    with build_client(service) as client:
        try:
            response = client.get(
                url=document_url,
                headers={  # TODO: improve the way we set the headers
                    "Audit-User-Representation": "GGP-Zoeken (system)",
                    "Audit-User-ID": "GPP-Zoeken",
                    "Audit-Remarks": "download document for indexing.",
                },
            )
            response.raise_for_status()
        except requests.RequestException:
            logger.exception("Could not download the document at %s.", document_url)
            return

    return base64.b64encode(response.content).decode("ascii")


@app.task()
def index_document(
    uuid: str,
    publicatie: str,
    informatie_categorieen: list[InformatieCategorieType],
    publisher: PublisherType,
    identifier: str,
    officiele_titel: str,
    verkorte_titel: str,
    omschrijving: str,
    creatiedatum: date,
    registratiedatum: datetime,
    laatst_gewijzigd_datum: datetime,
    download_url: str = "",
    file_size: int | None = None,
):
    document = Document(
        _id=uuid,
        uuid=uuid,
        publicatie=publicatie,
        informatie_categorieen=informatie_categorieen,
        publisher=publisher,
        identifier=identifier,
        officiele_titel=officiele_titel,
        verkorte_titel=verkorte_titel,
        omschrijving=omschrijving,
        creatiedatum=creatiedatum,
        registratiedatum=registratiedatum,
        laatst_gewijzigd_datum=laatst_gewijzigd_datum,
    )

    if (
        download_url
        and file_size
        and file_size <= settings.SEARCH_INDEX["MAX_INDEX_FILE_SIZE"]
    ):
        document.document_data = _download_document(document_url=download_url)

    with get_client() as client:
        document.save(
            using=client,
            refresh=settings.SEARCH_INDEX["REFRESH"],
            pipeline=DOCUMENT_ATTACHMENT_PIPELINE_ID,
        )


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
