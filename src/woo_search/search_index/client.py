from collections.abc import Collection, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, assert_never
from uuid import UUID

from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from .documents import Document, Publication

__all__ = ["get_client", "get_search_results"]


def get_client() -> Elasticsearch:
    username = settings.SEARCH_INDEX["USER"]
    password = settings.SEARCH_INDEX["PASSWORD"]
    basic_auth = (username, password) if username else None

    return Elasticsearch(
        settings.SEARCH_INDEX["HOST"],
        basic_auth=basic_auth,
        timeout=settings.SEARCH_INDEX["TIMEOUT"],
    )


type IndexName = Literal["publication", "document"]


@dataclass
class SearchResult:
    type: IndexName
    record: Document | Publication


@dataclass
class SearchResults:
    total_count: int
    results: Sequence[SearchResult]


QUERY_REPLACEMENTS = str.maketrans(
    {
        "+": r"\+",
        "-": r"\-",
        "=": r"\=",
        # can't be escaped at all, drop it
        ">": "",
        # can't be escaped at all, drop it
        "<": "",
        "!": r"\!",
        "(": r"\(",
        ")": r"\)",
        "{": r"\{",
        "}": r"\}",
        "[": r"\[",
        "]": r"\]",
        "^": r"\^",
        '"': r"\"",
        "~": r"\~",
        "*": r"\*",
        "?": r"\?",
        ":": r"\:",
        "\\": "\\\\",
        "/": r"\/",
    }
)


def clean_query(query: str) -> str:
    """
    The query_string query has some reserved characters that need to be escaped.

    See https://www.elastic.co/guide/en/elasticsearch/reference/8.17/query-dsl-query-string-query.html#_reserved_characters
    """
    # first pass - single character replacements
    query = query.translate(QUERY_REPLACEMENTS)
    # multi-character replacements
    return query.replace("&&", r"\&&").replace("||", r"\||")


def get_search_results(
    query: str,
    publishers: Collection[UUID],
    information_categories: Collection[UUID],
    result_type: IndexName | None = None,
    registration_date_from: datetime | None = None,
    registration_date_to: datetime | None = None,
    last_modified_from: datetime | None = None,
    last_modified_to: datetime | None = None,
    page: int = 1,
    page_size: int = 10,
    sort: Literal["relevance", "chronological"] = "relevance",
) -> SearchResults:
    """
    Perform the search query in elastic search.

    The filter/query parameters are translated into an Elastic Search query,
    which is executed agains the configured ES cluster. The results are then
    collected and returned so they can be post-processed if needed.

    :arg query: The search terms entered by the user. These may contain double quotes
      for exact matches and/or the AND/OR operators. See
      https://www.elastic.co/guide/en/elasticsearch/reference/8.17/query-dsl-query-string-query.html
      for all the details on how ES processes this.
    :arg publishers: A collection of publisher UUIDs. If provided, search results will
      be limited to provided publisher IDs.
    :arg information_categories: A collection of information category UUIDs. Only applies
      to the ``publication`` index, as this information is not stored for individual
      documents. If provided, search results will be limited to provided information
      category IDs.
    :arg result_type: Optionally restrict the search operation to an index. If not
      specified, all indices will be searched.
    :arg registration_date_from: If provided, only include documents that were
      registered after or on this timestamp.
    :arg registration_date_to: If provided, only include documents that were
      registered before or on this timestamp.
    :arg last_modified_from: If provided, only include documents that were
      last modified after or on this timestamp.
    :arg last_modified_to: If provided, only include documents that were
      last modified before or on this timestamp.
    """

    # build up the search object from the provided arguments
    search = Search().doc_type(Document, Publication)

    # restrict to particular index/indices
    match result_type:
        case "publication":
            search = search.index(Publication.Index.name)
        case "document":
            search = search.index(Document.Index.name)
        case None:
            search = search.doc_type(Publication.Index.name, Document.Index.name)
        case _:  # pragma: no cover
            assert_never(result_type)

    # process the query (terms)
    if query:
        search = search.query(
            "query_string",
            query=clean_query(query),
            fields=[
                "identifier^3",
                "officiele_titel^2",
                "verkorte_titel^1.5",
                "omschrijving",
            ],
            fuzziness=2,  # distance (1 is typically okay for typo's, two is more fuzzy)
        )

    # add ordering configuration. note that sorting on score defaults to DESC, see:
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html#_sort_order
    match sort:
        case "relevance":
            search = search.sort("_score", "-laatst_gewijzigd_datum")
        case "chronological":
            search = search.sort("-laatst_gewijzigd_datum", "_score")
        case _:  # pragma: no cover
            assert_never(sort)

    # and paginate it
    page_from = page_size * (page - 1)
    search = search[page_from : page_from + page_size]

    # bind it to the client containing the connection details
    with get_client() as client:
        search = search.using(client)
        response = search.execute()

    # process the results
    results = [
        SearchResult(
            type=hit.meta.index,
            # ES-DSL typing isn't fancy enough yet...
            record=hit,  # pyright: ignore[reportArgumentType]
        )
        for hit in response.hits
    ]

    return SearchResults(
        total_count=response.hits.total.value,  # pyright: ignore[reportAttributeAccessIssue]
        results=results,
    )
