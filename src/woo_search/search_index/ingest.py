from django.conf import settings

from elasticsearch import Elasticsearch


def setup_document_attachment_processor(client: Elasticsearch):
    return client.ingest.put_pipeline(
        id="document_attachment",
        description="Extract Document attachment information",
        processors=[
            {
                "attachment": {
                    "field": "document_data",
                    "properties": ["content"],
                    "remove_binary": True,
                    "ignore_missing": True,
                    "indexed_chars": settings.SEARCH_INDEX["INDEXED_CHARS"],
                }
            }
        ],
    )
