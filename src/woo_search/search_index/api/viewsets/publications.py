from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from woo_search.api.serializers import CeleryTaskIdSerializer

from ...tasks import (
    delete_document_index,
    delete_publication_index,
    index_document,
    index_publication,
)
from ...typing import DocumentType, PublicationType
from ..serializers import DocumentSerializer, PublicationSerializer


@extend_schema(tags=["index"])
@extend_schema_view(
    create=extend_schema(
        summary=_("Index document metadata."),
        description=_(
            "Index the received Document metadata from the Register API in Elasticsearch."
        ),
        responses={202: CeleryTaskIdSerializer},
    ),
    destroy=extend_schema(
        summary=_("Delete document metadata."),
        description=_(
            "Delete the Document index from the Register API in Elasticsearch."
        ),
        responses={204: None},
    ),
)
class DocumentViewSet(viewsets.ViewSet):
    serializer_class = DocumentSerializer
    lookup_field = "uuid"

    def create(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: DocumentType = serializer.validated_data
        save_document_task = index_document.delay(
            uuid=validated_data["uuid"],
            publicatie=validated_data["publicatie"],
            publisher=validated_data["publisher"],
            identifier=validated_data["identifier"],
            officiele_titel=validated_data["officiele_titel"],
            verkorte_titel=validated_data["verkorte_titel"],
            omschrijving=validated_data["omschrijving"],
            creatiedatum=validated_data["creatiedatum"],
            registratiedatum=validated_data["registratiedatum"],
            laatst_gewijzigd_datum=validated_data["laatst_gewijzigd_datum"],
        )

        return Response(
            data={"task_id": save_document_task.id}, status=status.HTTP_202_ACCEPTED
        )

    def destroy(self, request: Request, uuid: str):
        delete_document_index.delay(uuid=uuid)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["index"])
@extend_schema_view(
    create=extend_schema(
        summary=_("Index publication metadata."),
        description=_(
            "Index the received Publication metadata from the Register API in Elasticsearch."
        ),
        responses={202: CeleryTaskIdSerializer},
    ),
    destroy=extend_schema(
        summary=_("Delete document metadata."),
        description=_(
            "Delete the Publication index from the Register API in Elasticsearch."
        ),
        responses={204: None},
    ),
)
class PublicationViewSet(viewsets.ViewSet):
    serializer_class = PublicationSerializer
    lookup_field = "uuid"

    def create(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: PublicationType = serializer.validated_data
        publication_task = index_publication.delay(
            uuid=validated_data["uuid"],
            publisher=validated_data["publisher"],
            informatie_categorieen=validated_data["informatie_categorieen"],
            officiele_titel=validated_data["officiele_titel"],
            verkorte_titel=validated_data["verkorte_titel"],
            omschrijving=validated_data["omschrijving"],
            registratiedatum=validated_data["registratiedatum"],
            laatst_gewijzigd_datum=validated_data["laatst_gewijzigd_datum"],
        )

        return Response(
            data={"task_id": publication_task.id}, status=status.HTTP_202_ACCEPTED
        )

    def destroy(self, request: Request, uuid: str):
        delete_publication_index.delay(uuid=uuid)
        return Response(status=status.HTTP_204_NO_CONTENT)
