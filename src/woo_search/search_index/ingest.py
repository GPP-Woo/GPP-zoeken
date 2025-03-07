from django.conf import settings

from elasticsearch import Elasticsearch

from .constants import DOCUMENT_ATTACHMENT_PIPELINE_ID


def setup_document_attachment_processor(client: Elasticsearch) -> bool:
    """
    Setup up attachment processor for the documents index.
    Returns true or false depending on if the ingest pipline is acknowledged or not.
    """
    response = client.ingest.put_pipeline(
        id=DOCUMENT_ATTACHMENT_PIPELINE_ID,
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
    assert hasattr(response, "body"), "body not present in response"

    return bool(response.body.get("acknowledged"))
