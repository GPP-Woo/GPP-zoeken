import logging

from django.apps import AppConfig

from elasticsearch.exceptions import ConnectionError

from .client import get_client
from .documents import Document

logger = logging.getLogger(__name__)


class IndexConfig(AppConfig):
    name = "woo_search.search_index"

    def ready(self):
        if client := get_client():
            try:
                if not client.indices.exists(index="document"):
                    Document().init(using=client)
            except ConnectionError:
                logger.warning("Could not connect to Elasticsearch")
