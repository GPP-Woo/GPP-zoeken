from woo_search.celery import app
from woo_search.index.documents import Document


@app.task()
def index_document(data: dict):
    Document.init()
    Document(meta=data, **data).save()
