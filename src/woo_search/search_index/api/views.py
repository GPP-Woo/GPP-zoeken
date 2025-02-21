from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from ..client import get_search_results
from ..typing import SearchParameters
from .serializers import SearchResponseSerializer, SearchSerializer


@extend_schema(
    tags=["search"],
    summary=_("Search"),
    description=_("Search the publication and/or document records."),
    responses={200: SearchResponseSerializer(many=True)},
)
class SearchView(APIView):
    def post(self, request, *args, **kwargs):
        query_serializer = SearchSerializer(data=request.data)
        query_serializer.is_valid(raise_exception=True)

        params: SearchParameters = query_serializer.validated_data

        search_results = get_search_results(
            query=params["query"],
            publishers=[],
            information_categories=[],
            result_type=rt if (rt := params["result_type"]) != "*" else None,
            registration_date_from=None,
            registration_date_to=None,
            last_modified_from=None,
            last_modified_to=None,
            page=(page := params["page"]),
            page_size=(page_size := params["page_size"]),
            sort=params["sort"],
        )

        response = SearchResponseSerializer(
            instance=search_results,
            context={"page": page, "page_size": page_size},
        )
        return Response(response.data)
