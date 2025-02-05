from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.response import Response

from ...tasks import index_document
from ..serializers import DocumentSerializer


@extend_schema(tags=["Documenten"])
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
        index_document.delay(serializer.data)
        return Response(serializer.data)
