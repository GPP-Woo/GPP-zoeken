from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ..client import search
from ..typing import SearchType
from .serializers import SearchResponseSerializer, SearchSerializer


@extend_schema(
    tags=["index"],
    summary=_("Search"),
    description=_("Search the publication and document records."),
    responses={
        200: SearchResponseSerializer(many=True),
    },
)
class SearchView(APIView):
    def post(self, request, *args, **kwargs):
        query_serializer = SearchSerializer(data=request.data)
        query_serializer.is_valid(raise_exception=True)

        params: SearchType = query_serializer.validated_data

        data = search(params)
        data.update(
            {
                "previous": params.get("page") > 1,
                "next": params.get("page_size") * params.get("page") < data["count"],
            }
        )

        response = SearchResponseSerializer(data)
        return Response(response.data)
