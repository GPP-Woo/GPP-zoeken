import base64
import io
import logging
import zipfile
from datetime import date, datetime
from typing import TypedDict

from django.conf import settings

import magic
import py7zr
import requests
from elasticsearch import NotFoundError
from zgw_consumers.client import build_client
from zgw_consumers.models import Service

from woo_search.celery import app

from .client import get_client
from .constants import DOCUMENT_ATTACHMENT_PIPELINE_ID
from .index import Document, Publication, Topic
from .typing import NestedInformationCategoryType, NestedPublisherType, NestedTopicType

logger = logging.getLogger(__name__)

# TODO: replace this with some code which keeps in sync with gpp-app
SUPPORTED_FILE_MIMETYPES = [
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/html",
    "application/vnd.oasis.opendocument.formula",
    "application/vnd.oasis.opendocument.presentation",
    "application/vnd.oasis.opendocument.spreadsheet",
    "application/vnd.oasis.opendocument.text",
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.presentationml.slideshow",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.ms-powerpoint.slideshow.macroEnabled.12",
    "application/rtf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
]


class DocumentData(TypedDict):
    document_data: str


type NestedDocumentData = list[DocumentData]


def _check_and_retrieve_document_data(
    file, total_file_size
) -> tuple[DocumentData | None, int]:
    document_mime = magic.from_buffer(file.read(2048), mime=True)
    file_size = file.__sizeof__()

    if document_mime in SUPPORTED_FILE_MIMETYPES:
        file.seek(0)

        if total_file_size + file_size <= settings.SEARCH_INDEX["MAX_INDEX_FILE_SIZE"]:
            total_file_size += file_size

            return {
                "document_data": base64.b64encode(file.read()).decode("ascii")
            }, total_file_size

    return None, total_file_size


def _get_zip_content(document_file: io.BytesIO) -> NestedDocumentData:
    file_list: NestedDocumentData = []
    total_file_size = 0

    with zipfile.ZipFile(file=document_file, mode="r") as zip_file:
        for file_name in zip_file.namelist():
            with zip_file.open(file_name) as file:
                document_data, total_file_size = _check_and_retrieve_document_data(
                    file, total_file_size
                )
                if document_data:
                    file_list.append(document_data)

    return file_list


def _get_7z_content(document_file: io.BytesIO) -> NestedDocumentData:
    file_list: NestedDocumentData = []
    total_file_size = 0

    with py7zr.SevenZipFile(document_file, mode="r") as zip_file:
        if zip_file_dict := zip_file.readall():
            for file in zip_file_dict.values():
                document_data, total_file_size = _check_and_retrieve_document_data(
                    file, total_file_size
                )
                if document_data:
                    file_list.append(document_data)

    return file_list


def _download_document(document_url: str) -> NestedDocumentData | None:
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

    with io.BytesIO(initial_bytes=response.content) as document_file:
        document_mime = magic.from_buffer(document_file.read(2048), mime=True)
        document_file.seek(0)

        match document_mime:
            case "application/zip":
                return _get_zip_content(document_file)
            # Don't need extra introspection like open-forms (gh #4658)
            # Because we only rely on magic type and not the received content_type
            case "application/x-7z-compressed":
                return _get_7z_content(document_file)
            case _:
                return [
                    {
                        "document_data": base64.b64encode(response.content).decode(
                            "ascii"
                        )
                    }
                ]


@app.task()
def index_document(
    uuid: str,
    publicatie: str,
    informatie_categorieen: list[NestedInformationCategoryType],
    onderwerpen: list[NestedTopicType],
    publisher: NestedPublisherType,
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
        onderwerpen=onderwerpen,
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
    publisher: NestedPublisherType,
    informatie_categorieen: list[NestedInformationCategoryType],
    onderwerpen: list[NestedTopicType],
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
        onderwerpen=onderwerpen,
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


@app.task()
def index_topic(
    uuid: str,
    officiele_titel: str,
    omschrijving: str,
    registratiedatum: datetime,
    laatst_gewijzigd_datum: datetime,
):
    topic = Topic(
        _id=uuid,
        uuid=uuid,
        officiele_titel=officiele_titel,
        omschrijving=omschrijving,
        registratiedatum=registratiedatum,
        laatst_gewijzigd_datum=laatst_gewijzigd_datum,
    )

    with get_client() as client:
        topic.save(using=client, refresh=settings.SEARCH_INDEX["REFRESH"])


@app.task()
def remove_topic_from_index(uuid: str) -> None:
    """
    If the topic with specified ``uuid`` is present in the index, remove it.

    :arg uuid: The ID of the topic in Elastic Search.
    """
    with get_client() as client:
        try:
            topic = Topic.get(using=client, id=uuid)
            assert topic is not None
        except NotFoundError as exc:
            logger.info("Topic with ID %s not found, aborting.", uuid, exc_info=exc)
            return
        else:
            topic.delete(using=client)
