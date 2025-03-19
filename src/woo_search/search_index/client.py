import os
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal, assert_never
from urllib.parse import urlsplit
from uuid import UUID

from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q, Search

from .index import Document, Publication
from .typing import IndexName

__all__ = ["get_client", "get_search_results"]


def get_client() -> Elasticsearch:
    host = settings.SEARCH_INDEX["HOST"]
    username = settings.SEARCH_INDEX["USER"]
    password = settings.SEARCH_INDEX["PASSWORD"]
    basic_auth = (username, password) if username else None

    # REQUESTS_CA_BUNDLE is set by self-certifi OR could be set at deployment time, acts
    # as default if no explicit CA is specified.
    ca_certs: str | None = settings.SEARCH_INDEX["CA_CERTS"] or os.environ.get(
        "REQUESTS_CA_BUNDLE"
    )

    # can't just fallback to ca_certs=None since it has special meaning
    extra = {}
    if ca_certs and urlsplit(host).scheme == "https":  # pragma: no cover
        extra["ca_certs"] = ca_certs

    return Elasticsearch(
        host,
        basic_auth=basic_auth,
        timeout=settings.SEARCH_INDEX["TIMEOUT"],
        **extra,
    )


@dataclass
class SearchResult:
    type: IndexName
    record: Document | Publication


@dataclass
class ResultTypeBucket:
    result_type: IndexName
    count: int


@dataclass
class PublisherBucket:
    name: str
    uuid: UUID
    count: int


@dataclass
class InformationCategoryBucket:
    name: str
    uuid: UUID
    count: int


@dataclass
class SearchResults:
    total_count: int
    results: Sequence[SearchResult]
    result_type_buckets: Sequence[ResultTypeBucket]
    publisher_buckets: Sequence[PublisherBucket]
    information_category_buckets: Sequence[InformationCategoryBucket]


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
    # query
    query: str,
    # filters
    publishers: Collection[UUID],
    information_categories: Collection[UUID],
    result_type: IndexName | None = None,
    registration_date_from: datetime | None = None,
    registration_date_to: datetime | None = None,
    last_modified_from: datetime | None = None,
    last_modified_to: datetime | None = None,
    creatiedatum_from: date | None = None,
    creatiedatum_to: date | None = None,
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
      registered before this timestamp.
    :arg last_modified_from: If provided, only include documents that were
      last modified after or on this timestamp.
    :arg last_modified_to: If provided, only include documents that were
      last modified before this timestamp.
    :arg creatiedatum_from: If provided, only include documents that have a
      creatiedatum after or on this date. Requires ``result_type`` to be set to
      ``"document"``.
    :arg creatiedatum_to: If provided, only include documents that have a
      creatiedatum before or on this date. Requires ``result_type`` to be set to
      ``"document"``.
    :arg page: The page number of results to retrieve. Counting starts at ``1``.
    :arg page_size: The number of results to return within a single page.
    :arg sort: Sort order to apply to the results. Relevance orders by score (from best
      to worst), chronological orders by last modification date.
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
            search = search.index(Publication.Index.name, Document.Index.name).extra(
                indices_boost=[
                    {Publication.Index.name: 2.0},
                    {Document.Index.name: 1.0},
                ]
            )
        case _:  # pragma: no cover
            assert_never(result_type)

    # process the query (terms)
    if query:
        search = search.query(
            "simple_query_string",
            query=query,
            fields=[
                "identifier^3",
                "officiele_titel^2",
                "verkorte_titel^1.5",
                "omschrijving^1.2",
                "attachment.content",
            ],
            flags="OR|AND|PHRASE|PRECEDENCE|WHITESPACE",
            default_operator="AND",
        )

    # process the date filters
    if registration_date_from or registration_date_to:
        # as soon as one bound is given, construct the filter
        search = search.filter(
            "range",
            registratiedatum={
                "gte": registration_date_from,
                "lt": registration_date_to,
            },
        )

    if last_modified_from or last_modified_to:
        # as soon as one bound is given, construct the filter
        search = search.filter(
            "range",
            laatst_gewijzigd_datum={
                "gte": last_modified_from,
                "lt": last_modified_to,
            },
        )

    if creatiedatum_from or creatiedatum_to:
        assert result_type == "document"
        search = search.filter(
            "range",
            creatiedatum={"gte": creatiedatum_from, "lte": creatiedatum_to},
        )

    publisher_filter = (
        Q("terms", publisher__uuid__keyword=[str(item) for item in publishers])
        if publishers
        else None
    )
    if publisher_filter:
        search = search.post_filter(publisher_filter)

    information_categories_filter = (
        Q(
            "nested",
            path="informatie_categorieen",
            query=Q(
                "terms",
                informatie_categorieen__uuid__keyword=[
                    str(item) for item in information_categories
                ],
            ),
        )
        if information_categories
        else None
    )
    if information_categories_filter is not None:
        search = search.post_filter(information_categories_filter)

    # now, add the boosting via decay function to favour recently added documents over
    # older ones. Docs:
    # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html#gauss-decay
    search.query = Q(  # pyright: ignore[reportAttributeAccessIssue]
        "function_score",
        query=search.query or Q("match_all"),
        functions=[
            {
                "gauss": {
                    "registratiedatum": {
                        "origin": "now",
                        "scale": "15d",  # after ~two weeks, the decay will be 0.5
                        "offset": "7d",  # only start appylying decay to documents older than a week
                        "decay": 0.5,
                    }
                }
            }
        ],
        score_mode="multiply",
    )

    # add aggregations
    search.aggs.bucket("ResultType", "terms", field="_index")

    search.aggs.bucket(
        "Publisher",
        "filter",
        filter=information_categories_filter or Q("match_all"),
    ).bucket(
        "FilteredPublisher",
        "multi_terms",
        terms=[
            {"field": "publisher.uuid.keyword"},
            {"field": "publisher.naam.keyword"},
        ],
    )

    search.aggs.bucket(
        "InformationCategories", "filter", filter=publisher_filter or Q("match_all")
    ).bucket(
        "Categories",
        "nested",
        path="informatie_categorieen",
    ).bucket(
        "FilteredCategories",
        "multi_terms",
        terms=[
            {"field": "informatie_categorieen.uuid.keyword"},
            {"field": "informatie_categorieen.naam.keyword"},
        ],
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

    aggs = response.aggregations
    return SearchResults(
        total_count=response.hits.total.value,  # pyright: ignore[reportAttributeAccessIssue]
        results=results,
        result_type_buckets=[
            ResultTypeBucket(result_type=bucket.key, count=bucket.doc_count)
            for bucket in aggs.ResultType.buckets
        ],
        publisher_buckets=[
            PublisherBucket(
                # items are ordered by the fields specified in the aggregation
                uuid=UUID(bucket.key[0]),
                name=bucket.key[1],
                count=bucket.doc_count,
            )
            for bucket in aggs.Publisher.FilteredPublisher.buckets
        ],
        information_category_buckets=[
            InformationCategoryBucket(
                # items are ordered by the fields specified in the aggregation
                uuid=UUID(bucket.key[0]),
                name=bucket.key[1],
                count=bucket.doc_count,
            )
            for bucket in aggs.InformationCategories.Categories.FilteredCategories.buckets
        ],
    )
