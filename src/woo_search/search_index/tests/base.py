import logging
from collections.abc import Collection

from django.test import TestCase, override_settings, tag

from elasticsearch_dsl import Document
from rest_framework.test import APITestCase

from woo_search.conf.utils import config
from woo_search.search_index.client import get_client

from ..utils import get_index_document_types

CI = config("CI", default=False)  # Github actions sets this to True

logger = logging.getLogger(__name__)

override_es_settings = override_settings(
    SEARCH_INDEX={
        "HOST": "http://localhost:9201",
        "USER": "",
        "PASSWORD": "",
        "TIMEOUT": 3,
        "REFRESH": "wait_for",
    }
)


class ElasticSearchMixin:
    """
    Handles setting up test data for Elasticsearch Documents by creating test
    indexes.
    """

    _es_online: bool = True
    _es_indexes: set[str]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # pyright: ignore[reportAttributeAccessIssue]

        _index_names: set[str] = set()
        _document_types: Collection[type[Document]] = []
        for subcls in get_index_document_types():
            _index_names.add(subcls.Index.name)
            _document_types.append(subcls)

        cls._es_indexes = _index_names

        # create the indices
        with override_es_settings:
            with get_client() as client:
                cls._es_online = client.ping()
                if not cls._es_online:
                    level = logging.WARNING if not CI else logging.DEBUG
                    logger.log(
                        level,
                        "ES %r is not available. Running in CI: %r.%s",
                        client,
                        CI,
                        (
                            ""
                            if CI
                            else " Use `docker/docker-compose.es.yml` to spin up the service."
                        ),
                    )
                else:
                    for _doc_type in _document_types:
                        # create index and mappings
                        _doc_type.init(using=client)

        def teardown():
            if not cls._es_online:
                return

            with override_es_settings:
                with get_client() as client:
                    client.indices.delete(index=list(_index_names))

        cls.addClassCleanup(teardown)  # pyright: ignore[reportAttributeAccessIssue]

    def setUp(self) -> None:
        super().setUp()  # pyright: ignore[reportAttributeAccessIssue]

        if not self._es_online:
            return

        with override_es_settings:
            with get_client() as client:
                # empty index before tests
                client.delete_by_query(
                    index=list(self._es_indexes),
                    body={"query": {"match_all": {}}},
                    refresh=True,
                )


@tag("elasticsearch")
@override_es_settings
class ElasticSearchTestCase(ElasticSearchMixin, TestCase):
    """
    Django TestCase subclass with setup and teardown for elastic search cluster.
    """


@tag("elasticsearch")
@override_es_settings
class ElasticSearchAPITestCase(ElasticSearchMixin, APITestCase):
    """
    DRC APITestCase subclass with setup and teardown for elastic search cluster.
    """
