from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from woo_search.api.permissions import TokenAuthReadPermission

from ..client import get_search_results
from ..typing import SearchParameters
from .serializers import SearchResponseSerializer, SearchSerializer


class SearchView(APIView):
    permission_classes = (TokenAuthReadPermission,)

    @extend_schema(
        tags=["search"],
        summary=_("Search"),
        operation_id="search",
        description=_("Search the publication and/or document records."),
        request=SearchSerializer,
        responses={200: SearchResponseSerializer(many=True)},
    )
    def post(self, request, *args, **kwargs):
        query_serializer = SearchSerializer(data=request.data)
        query_serializer.is_valid(raise_exception=True)

        params: SearchParameters = query_serializer.validated_data

        search_results = get_search_results(
            query=params["query"],
            publishers=params["publishers"],
            information_categories=params["informatie_categorieen"],
            result_types=params["result_types"],
            registration_date_from=params["registratiedatum_vanaf"],
            registration_date_to=params["registratiedatum_tot"],
            last_modified_from=params["laatst_gewijzigd_datum_vanaf"],
            last_modified_to=params["laatst_gewijzigd_datum_tot"],
            creatiedatum_from=params["creatiedatum_vanaf"],
            creatiedatum_to=params["creatiedatum_tot_en_met"],
            page=(page := params["page"]),
            page_size=(page_size := params["page_size"]),
            sort=params["sort"],
        )

        response = SearchResponseSerializer(
            instance=search_results,
            context={"page": page, "page_size": page_size},
        )
        return Response(response.data)
