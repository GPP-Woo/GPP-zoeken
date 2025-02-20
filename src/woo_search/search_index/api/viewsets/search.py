from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from woo_search.search_index.api.serializers import (
    SearchResponseSerializer,
    SearchSerializer,
)

from ...client import get_client
from ...constants import SortChoices
from ...typing import SearchType


@extend_schema(
    tags=["index"],
    summary=_("Search"),
    description=_("Search the publication and document records."),
    responses={
        200: SearchResponseSerializer(many=True),
    },
)
class SearchView(APIView):
    serializer_class = SearchSerializer
    response_serializer_class = SearchResponseSerializer

    def _query_multi_match(self, query: str):
        return {
            "multi_match": {
                "fields": [
                    "officiele_titel^2",
                    "verkorte_titel^1.5",
                    "omschrijving",
                    "identifier^3",
                ],
                "fuzziness": 1,
                "query": query,
            }
        }

    def _build_must(self, params: SearchType):
        must = []

        if query := params.get("query"):
            must.append(self._query_multi_match(query))

        return must

    def base_search_query(self, params: SearchType):
        return {
            "index": params.get("result_type"),
            "size": params.get("page_size"),
            "from": params.get("page"),
            "track_total_hits": True,
        }

    def search_query(self, params: SearchType):
        search = self.base_search_query(params)

        if sort := params.get("sort"):
            sort_order = [
                {"_score": {"order": "desc"}},
                {"laatst_gewijzigd_datum": {"order": "desc"}},
            ]

            match sort:
                case SortChoices.chronological:
                    search["sort"] = sort_order[::-1]
                case SortChoices.relevance:
                    search["sort"] = sort_order

        if must_query := self._build_must(params):
            search["query"] = {"bool": {"must": must_query}}

        return search

    def post(self, request, *args, **kwargs):
        query_serializer: SearchSerializer = self.serializer_class(data=request.data)
        query_serializer.is_valid(raise_exception=True)

        params: SearchType = query_serializer.validated_data
        search = self.search_query(params)

        with get_client() as client:
            es_data = client.search(**search)

        es_hits = es_data["hits"]["hits"]

        results = []
        for record in es_hits:
            results.append(
                {
                    "type": record["_index"],
                    "record": record["_source"],
                }
            )

        data = {
            "count": len(es_hits),
            # if not `from` 0 then we got a previous page.
            "previous": params.get("page") > 0,
            # if the current `from` with the next amount of indexes that will be skipped
            # is lower than the total amount then there is no next page.
            "next": params.get("page") + params.get("page_size")
            < es_data["hits"]["total"]["value"],
            "results": results,
        }

        response = self.response_serializer_class(data)
        return Response(response.data)
