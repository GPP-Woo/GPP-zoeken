from woo_search.celery import app

from ..client import get_client
from ..documents import Document


@app.task()
def save_document(data: dict):
    document = Document(_id=data["uuid"], **data)
    with get_client() as client:
        document.save(using=client)
