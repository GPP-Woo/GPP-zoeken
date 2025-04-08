from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from woo_search.api.serializers import CeleryTaskIdSerializer

from ..tasks import (
    index_document,
    index_publication,
    remove_document_from_index,
    remove_publication_from_index,
)
from ..typing import DocumentIndexType, PublicationType
from .serializers import DocumentIndexSerializer, PublicationSerializer


@extend_schema(tags=["index"])
class DocumentViewSet(viewsets.ViewSet):
    serializer_class = DocumentIndexSerializer
    lookup_field = "uuid"

    @extend_schema(
        summary=_("Index document metadata."),
        description=_(
            "Index the received document metadata from the Register API in Elasticsearch."
        ),
        responses={202: CeleryTaskIdSerializer},
    )
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: DocumentIndexType = serializer.validated_data

        save_document_task = index_document.delay(
            uuid=validated_data["uuid"],
            publicatie=validated_data["publicatie"],
            informatie_categorieen=validated_data["informatie_categorieen"],
            onderwerpen=validated_data["onderwerpen"],
            publisher=validated_data["publisher"],
            identifier=validated_data["identifier"],
            officiele_titel=validated_data["officiele_titel"],
            verkorte_titel=validated_data["verkorte_titel"],
            omschrijving=validated_data["omschrijving"],
            creatiedatum=validated_data["creatiedatum"],
            registratiedatum=validated_data["registratiedatum"],
            laatst_gewijzigd_datum=validated_data["laatst_gewijzigd_datum"],
            download_url=validated_data["download_url"],
            file_size=validated_data["file_size"],
        )

        return Response(
            data={"task_id": save_document_task.id}, status=status.HTTP_202_ACCEPTED
        )

    @extend_schema(
        summary=_("Remove document from index."),
        description=_(
            "Remove the referenced document data from the index.\n"
            "Note that this schedules a background task to perform the actual removal."
        ),
        responses={202: CeleryTaskIdSerializer},
    )
    def destroy(self, request: Request, uuid: str):
        result = remove_document_from_index.delay(uuid=uuid)
        return Response(data={"task_id": result.id}, status=status.HTTP_202_ACCEPTED)


@extend_schema(tags=["index"])
class PublicationViewSet(viewsets.ViewSet):
    serializer_class = PublicationSerializer
    lookup_field = "uuid"

    @extend_schema(
        summary=_("Index publication metadata."),
        description=_(
            "Index the received publication metadata from the Register API in Elasticsearch."
        ),
        responses={202: CeleryTaskIdSerializer},
    )
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data: PublicationType = serializer.validated_data
        publication_task = index_publication.delay(
            uuid=validated_data["uuid"],
            publisher=validated_data["publisher"],
            informatie_categorieen=validated_data["informatie_categorieen"],
            onderwerpen=validated_data["onderwerpen"],
            officiele_titel=validated_data["officiele_titel"],
            verkorte_titel=validated_data["verkorte_titel"],
            omschrijving=validated_data["omschrijving"],
            registratiedatum=validated_data["registratiedatum"],
            laatst_gewijzigd_datum=validated_data["laatst_gewijzigd_datum"],
        )

        return Response(
            data={"task_id": publication_task.id}, status=status.HTTP_202_ACCEPTED
        )

    @extend_schema(
        summary=_("Remove publication from index."),
        description=_(
            "Remove the referenced publication data from the index.\n"
            "Note that this schedules a background task to perform the actual removal."
        ),
        responses={202: CeleryTaskIdSerializer},
    )
    def destroy(self, request: Request, uuid: str):
        result = remove_publication_from_index.delay(uuid=uuid)
        return Response(data={"task_id": result.id}, status=status.HTTP_202_ACCEPTED)
