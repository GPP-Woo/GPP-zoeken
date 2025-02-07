from woo_search.celery import app

from ..client import get_client
from ..documents import Document


@app.task()
def save_document(data: dict):
    document = Document(
        meta={"id": data["uuid"]}, **data  # pyright: ignore reportCallIssue
    )
    document.save(using=get_client())
