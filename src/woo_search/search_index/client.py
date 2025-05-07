import operator
import os
import re
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from functools import reduce
from typing import Literal, assert_never
from urllib.parse import urlsplit
from uuid import UUID

from django.conf import settings

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q, Query, Search

from .constants import ResultTypeChoices
from .index import Document, Publication, Topic
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
    record: Document | Publication | Topic


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
class TopicBucket:
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
    topic_buckets: Sequence[TopicBucket]
    information_category_buckets: Sequence[InformationCategoryBucket]


def clean_str_query(query: str) -> str:
    """
    Make the query suitable for ``simple_query_string`` search.

    While the ``query_string`` supports ``AND`` and ``OR`` out of the box, the
    ``simple_query_string`` does not appear to do so and requires us to convert
    this into the proper boolean operators (``+`` and ``|``).
    """
    # Pattern matches either a quoted substring (including quotes) or non-quote parts.
    pattern = r'"[^"]*"|[^"]+'
    parts: list[str] = re.findall(pattern, query)

    processed_parts = []
    for part in parts:
        # If the part starts and ends with a quote, assume it's a quoted phrase and
        # leave it unchanged.
        if part.startswith('"') and part.endswith('"'):
            processed_parts.append(part)
        else:
            # Replace standalone AND/OR with +/| using word boundaries.
            part = re.sub(r"\bAND\b", "+", part)
            part = re.sub(r"\bOR\b", "|", part)
            processed_parts.append(part)

    return "".join(processed_parts)


def _combine_queries(*queries: Query | None) -> Query:
    """
    Combine the provided filters into a single filter by AND'ing them together.

    If no filters are provided (i.e. they're all ``None``), a query to match everything
    is returned.
    """
    non_empty_queries = [query for query in queries if query is not None]
    if not non_empty_queries:
        return Q("match_all")
    return reduce(operator.and_, non_empty_queries)


def get_search_results(
    # query
    query: str,
    # filters
    publishers: Collection[UUID],
    information_categories: Collection[UUID],
    topics: Collection[UUID],
    result_types: Collection[IndexName] | None = None,
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
    :arg information_categories: A collection of information category UUIDs. Only
      applies to the ``publication`` index, as this information is not stored for
      individual documents. If provided, search results will be limited to provided
      information category IDs.
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
    search = (
        Search()
        .doc_type(Document, Publication, Topic)
        .index(Publication.Index.name, Document.Index.name, Topic.Index.name)
        .extra(
            indices_boost=[
                {Topic.Index.name: 3.0},
                {Publication.Index.name: 2.0},
                {Document.Index.name: 1.0},
            ]
        )
    )

    # process the query (terms)
    if query:
        search = search.query(
            "simple_query_string",
            query=clean_str_query(query),
            fields=[
                "identifier^3",
                "officiele_titel^2",
                "verkorte_titel^1.5",
                "omschrijving^1.2",
                "document_data.attachment.content",
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
        assert result_types == ["document"]
        search = search.filter(
            "range",
            creatiedatum={"gte": creatiedatum_from, "lte": creatiedatum_to},
        )

    result_type_filter = Q("terms", _index=result_types) if result_types else None
    if result_type_filter:
        search = search.post_filter(result_type_filter)

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

    topics_filter = (
        Q(
            "nested",
            path="onderwerpen",
            query=Q(
                "terms",
                onderwerpen__uuid__keyword=[str(item) for item in topics],
            ),
        )
        if topics
        else None
    )
    if topics_filter is not None:
        search = search.post_filter(topics_filter)

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
                        # after ~two weeks, the decay will be 0.5
                        "scale": "15d",
                        # only start appylying decay to documents older than a week
                        "offset": "7d",
                        "decay": 0.5,
                    }
                }
            }
        ],
        score_mode="multiply",
    )

    # add aggregations
    search.aggs.bucket(
        "ResultType",
        "filter",
        filter=_combine_queries(
            information_categories_filter,
            topics_filter,
            publisher_filter,
        ),
    ).bucket(
        "FilteredResultType",
        "terms",
        field="_index",
    )

    search.aggs.bucket(
        "Publisher",
        "filter",
        filter=_combine_queries(
            information_categories_filter,
            topics_filter,
            result_type_filter,
        ),
    ).bucket(
        "FilteredPublisher",
        "multi_terms",
        terms=[
            {"field": "publisher.uuid.keyword"},
            {"field": "publisher.naam.keyword"},
        ],
    )

    search.aggs.bucket(
        "InformationCategories",
        "filter",
        filter=_combine_queries(
            publisher_filter,
            topics_filter,
            result_type_filter,
        ),
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

    search.aggs.bucket(
        "Topics",
        "filter",
        filter=_combine_queries(
            information_categories_filter,
            publisher_filter,
            result_type_filter,
        ),
    ).bucket(
        "Topics",
        "nested",
        path="onderwerpen",
    ).bucket(
        "FilteredTopics",
        "multi_terms",
        terms=[
            {"field": "onderwerpen.uuid.keyword"},
            {"field": "onderwerpen.officiele_titel.keyword"},
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

    # The ordered list of result types we want to limit and order the
    # result_type_buckets
    ordered_bucket_result_types: list[ResultTypeChoices] = [
        ResultTypeChoices.topic,
        ResultTypeChoices.publication,
        ResultTypeChoices.document,
    ]

    return SearchResults(
        total_count=response.hits.total.value,  # pyright: ignore[reportAttributeAccessIssue]
        results=results,
        result_type_buckets=[
            ResultTypeBucket(result_type=bucket.key, count=bucket.doc_count)
            for bucket in sorted(
                aggs.ResultType.FilteredResultType.buckets,
                key=lambda bucket: ordered_bucket_result_types.index(bucket.key),
            )
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
            for bucket in (
                aggs.InformationCategories.Categories.FilteredCategories.buckets
            )
        ],
        topic_buckets=[
            TopicBucket(
                # items are ordered by the fields specified in the aggregation
                uuid=UUID(bucket.key[0]),
                name=bucket.key[1],
                count=bucket.doc_count,
            )
            for bucket in aggs.Topics.Topics.FilteredTopics.buckets
        ],
    )
