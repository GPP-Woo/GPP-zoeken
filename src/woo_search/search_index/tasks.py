import base64
import io
import logging
import warnings
import zipfile
from collections.abc import Callable, Iterator
from datetime import date, datetime
from typing import IO, TypedDict

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


class DocumentData(TypedDict):
    document_data: str


type NestedDocumentData = list[DocumentData]


type FileMeta = tuple[IO[bytes], int]


def _iter_zip_content(document_file: io.BytesIO) -> Iterator[FileMeta]:
    with zipfile.ZipFile(file=document_file, mode="r") as zip_file:
        for info in zip_file.infolist():
            with zip_file.open(info.filename) as file:
                yield file, info.file_size


def _iter_7z_content(document_file: io.BytesIO) -> Iterator[FileMeta]:
    with py7zr.SevenZipFile(document_file, mode="r") as zip_file:
        if not (zip_file_dict := zip_file.readall()):
            return
        filesizes: dict[str, int] = {
            file_info.filename: file_info.uncompressed for file_info in zip_file.list()
        }
        for name, file in zip_file_dict.items():
            yield file, filesizes[name]


def _extract_documents(
    document_file: io.BytesIO,
    iter_archive: Callable[[io.BytesIO], Iterator[FileMeta]],
) -> NestedDocumentData:
    file_list: NestedDocumentData = []
    total_size: int = 0

    for file, size_in_bytes in iter_archive(document_file):
        document_mime = magic.from_buffer(file.read(2048), mime=True)
        # NOTE: we deliberately do not recurse into nested archives, see
        # https://github.com/GPP-Woo/GPP-zoeken/pull/89#issuecomment-2890840775
        if document_mime not in settings.SEARCH_INDEXABLE_FILE_TYPES:
            logger.debug("file_skipped", extra={"mime_type": document_mime})
            continue

        # update the total size based on the non-base64 encoded file size - we don't
        # assign it yet because there may be smaller files that we can still stuff into
        # the document data
        new_total_size = total_size + size_in_bytes
        if new_total_size > settings.SEARCH_INDEX["MAX_INDEX_FILE_SIZE"]:
            logger.debug(
                "file_skipped", extra={"reason": "exceeding_max_index_file_size"}
            )
            continue

        # okay, we have headroom, prepare the file and next loop iteration
        total_size = new_total_size
        # now read the full file - there's still a risk if going OOM here if the
        # compression ratio is very high
        file.seek(0)
        file_contents = file.read()
        document_data = base64.b64encode(file_contents).decode("ascii")
        file_list.append({"document_data": document_data})

        # once our limit is reached, we can stop processing the archives entirely
        if total_size >= settings.SEARCH_INDEX["MAX_INDEX_FILE_SIZE"]:
            break

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

    _content_type = response.headers.get("Content-Type")

    with io.BytesIO(initial_bytes=response.content) as document_file:
        document_mime = magic.from_buffer(document_file.read(2048), mime=True)
        document_file.seek(0)

        # Arch Linux shared mimetypes doesn't properly detect application/zip :(
        if (
            document_mime == "application/octet-stream"
            and _content_type == "application/zip"
        ):  # pragma: no cover
            document_mime = "application/zip"

        match document_mime:
            case "application/zip":
                return list(_extract_documents(document_file, _iter_zip_content))
            # Don't need extra introspection like open-forms (gh #4658)
            # Because we only rely on magic type and not the received content_type
            case "application/x-7z-compressed":
                return list(_extract_documents(document_file, _iter_7z_content))
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
    *,
    uuid: str,
    publicatie: str,
    informatie_categorieen: list[NestedInformationCategoryType],
    onderwerpen: list[NestedTopicType],
    publisher: NestedPublisherType,
    identifiers: list[str],
    identifier: str = "",
    officiele_titel: str,
    verkorte_titel: str,
    omschrijving: str,
    creatiedatum: date,
    registratiedatum: datetime,
    gepubliceerd_op: datetime,
    laatst_gewijzigd_datum: datetime,
    download_url: str = "",
    file_size: int | None = None,
):
    if identifier:
        warnings.warn(
            "'identifier' is deprecated, use 'identifiers' list instead",
            DeprecationWarning,
            stacklevel=2,
        )
    document = Document(
        _id=uuid,
        uuid=uuid,
        publicatie=publicatie,
        informatie_categorieen=informatie_categorieen,
        onderwerpen=onderwerpen,
        publisher=publisher,
        identifier=identifier,
        identifiers=identifiers,
        officiele_titel=officiele_titel,
        verkorte_titel=verkorte_titel,
        omschrijving=omschrijving,
        creatiedatum=creatiedatum,
        registratiedatum=registratiedatum,
        gepubliceerd_op=gepubliceerd_op,
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
    *,
    uuid: str,
    publisher: NestedPublisherType,
    informatie_categorieen: list[NestedInformationCategoryType],
    onderwerpen: list[NestedTopicType],
    identifiers: list[str],
    officiele_titel: str,
    verkorte_titel: str,
    omschrijving: str,
    registratiedatum: datetime,
    gepubliceerd_op: datetime,
    laatst_gewijzigd_datum: datetime,
    datum_begin_geldigheid: datetime | None,
    datum_einde_geldigheid: datetime | None,
):
    publication = Publication(
        _id=uuid,
        uuid=uuid,
        publisher=publisher,
        informatie_categorieen=informatie_categorieen,
        onderwerpen=onderwerpen,
        identifiers=identifiers,
        officiele_titel=officiele_titel,
        verkorte_titel=verkorte_titel,
        omschrijving=omschrijving,
        registratiedatum=registratiedatum,
        gepubliceerd_op=gepubliceerd_op,
        laatst_gewijzigd_datum=laatst_gewijzigd_datum,
        datum_begin_geldigheid=datum_begin_geldigheid,
        datum_einde_geldigheid=datum_einde_geldigheid,
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
        gepubliceerd_op=registratiedatum,
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
