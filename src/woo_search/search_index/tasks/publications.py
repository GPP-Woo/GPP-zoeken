from woo_search.celery import app

from ..client import get_client
from ..documents import Document
from ..typing import DocumentType


@app.task()
def index_document(data: DocumentType):
    document = Document(_id=data["uuid"], **data)
    with get_client() as client:
        document.save(using=client)
