from django.conf import settings

from elasticsearch import Elasticsearch


def get_client() -> Elasticsearch:
    username = settings.SEARCH_INDEX["USER"]
    password = settings.SEARCH_INDEX["PASSWORD"]
    basic_auth = (username, password) if username else None

    return Elasticsearch(
        settings.SEARCH_INDEX["HOST"],
        basic_auth=basic_auth,
        timeout=settings.SEARCH_INDEX["TIMEOUT"],
    )
