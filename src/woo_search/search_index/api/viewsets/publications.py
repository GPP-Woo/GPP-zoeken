from django.utils.translation import gettext_lazy as _

from dateutil import parser
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.response import Response

from ...tasks import index_document
from ...typing import DocumentType
from ..serializers import DocumentSerializer


@extend_schema(tags=["index"])
@extend_schema_view(
    create=extend_schema(
        summary=_("Index document metadata."),
        description=_(
            "Index the received document metadata from the Register API in Elasticsearch."
        ),
    ),
)
class DocumentViewSet(viewsets.ViewSet):
    serializer_class = DocumentSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        es_data = self._parsed_es_data(serializer.data)
        save_document_task = index_document.delay(es_data)
        return Response(
            data={"task_id": save_document_task.id}, status=status.HTTP_202_ACCEPTED
        )

    def _parsed_es_data(self, data) -> DocumentType:
        data["creatiedatum"] = parser.parse(data["creatiedatum"])
        data["registratiedatum"] = parser.parse(data["registratiedatum"])
        data["laatst_gewijzigd_datum"] = parser.parse(data["laatst_gewijzigd_datum"])
        return data
