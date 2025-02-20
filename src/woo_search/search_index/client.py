from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q, Search

from .constants import SortChoices
from .typing import SearchType


def get_client() -> Elasticsearch:
    username = settings.SEARCH_INDEX["USER"]
    password = settings.SEARCH_INDEX["PASSWORD"]
    basic_auth = (username, password) if username else None

    return Elasticsearch(
        settings.SEARCH_INDEX["HOST"],
        basic_auth=basic_auth,
        timeout=settings.SEARCH_INDEX["TIMEOUT"],
    )


def _query_filter(query):
    return Q(
        "multi_match",
        query=query,
        fuzziness=1,
        fields=[
            "officiele_titel^2",
            "verkorte_titel^1.5",
            "omschrijving",
            "identifier^3",
        ],
    )


def _sort_filter(es_search: Search, sort_option: SortChoices):
    match sort_option:
        case SortChoices.relevance:
            return es_search.sort(
                {
                    "_score": {"order": "desc"},
                    "laatst_gewijzigd_datum": {"order": "desc"},
                },
            )
        case SortChoices.chronological:
            return es_search.sort(
                {
                    "laatst_gewijzigd_datum": {"order": "desc"},
                    "_score": {"order": "desc"},
                }
            )


def search(params: SearchType):
    with get_client() as client:
        es_search = Search(using=client, index=params.get("result_type"))

        es_search = _sort_filter(es_search, params.get("sort"))

        if query := params.get("query"):
            es_search = es_search.query(_query_filter(query))

        page = params.get("page")
        page_size = params.get("page_size")
        paginate_from = page_size * (page - 1)

        es_search = es_search[paginate_from:page_size]

        response = es_search.execute()

        results = []
        for hit in response.hits.hits:
            results.append(
                {
                    "type": hit["_index"],
                    "record": hit["_source"],
                }
            )

        return {
            "count": response.hits.total.value,
            "results": results,
        }
