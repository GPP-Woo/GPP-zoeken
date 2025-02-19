from datetime import date
from typing import List

from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from woo_search.search_index.api.serializers import (
    SearchResponseSerializer,
    SearchSerializer,
)

from ...client import get_client
from ...constants import ResultTypeChoices, SortChoices
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

    def _date_range(self, key: str, gte: date | None = None, lte: date | None = None):
        return {
            "range": {
                key: {
                    "gte": gte,
                    "lte": lte,
                }
            }
        }

    def _build_filter(self, params: SearchType):
        filter_list = []

        registratiedatum_vanaf = params.get("registratiedatum_vanaf")
        registratiedatum_tot = params.get("registratiedatum_tot")

        if any((registratiedatum_vanaf, registratiedatum_tot)):
            filter_list.append(
                self._date_range(
                    "registratiedatum",
                    gte=registratiedatum_vanaf,
                    lte=registratiedatum_tot,
                )
            )

        laatst_gewijzigd_datum_vanaf = params.get("laatst_gewijzigd_datum_vanaf")
        laatst_gewijzigd_datum_tot = params.get("laatst_gewijzigd_datum_tot")

        if any((laatst_gewijzigd_datum_vanaf, laatst_gewijzigd_datum_tot)):
            filter_list.append(
                self._date_range(
                    "laatst_gewijzigd_datum",
                    gte=laatst_gewijzigd_datum_vanaf,
                    lte=laatst_gewijzigd_datum_tot,
                )
            )

        creatiedatum_vanaf = params.get("creatiedatum_vanaf")
        creatiedatum_tot = params.get("creatiedatum_tot")

        if any((creatiedatum_vanaf, creatiedatum_tot)):
            filter_list.append(
                self._date_range(
                    "creatiedatum", gte=creatiedatum_vanaf, lte=creatiedatum_tot
                )
            )

        return filter_list

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

    def _publishers(self, publishers: List[str]):
        should_list = []

        for publisher_uuid in publishers:
            should_list.append(
                {
                    "match": {
                        "publisher.uuid": publisher_uuid,
                    }
                }
            )

        return {"bool": {"should": should_list}}

    def _build_must(self, params: SearchType):
        must = []

        if query := params.get("query"):
            must.append(self._query_multi_match(query))

        if publishers := params.get("publishers"):
            must.append(self._publishers(publishers))

        return must

    def _get_index(self, params: SearchType) -> ResultTypeChoices:
        if params.get("creatiedatum_vanaf") or params.get("creatiedatum_tot"):
            return ResultTypeChoices.document

        return params.get("result_type")

    def base_search_query(self, params: SearchType):
        return {
            "index": self._get_index(params),
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

        must_query = self._build_must(params)
        filter_query = self._build_filter(params)

        if must_query or filter_query:
            search["query"] = {"bool": {}}

            if must_query:
                search["query"]["bool"]["must"] = must_query

            if filter_query:
                search["query"]["bool"]["filter"] = filter_query

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
