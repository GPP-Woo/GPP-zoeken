from elasticsearch_dsl import Index, analyzer, tokenizer

from .client import get_client

ngram_analyzer = analyzer(
    "ngram_analyzer",
    tokenizer=tokenizer("ngram_tokenizer", "ngram", min_gram=2, max_gram=3),
)


def initialize_document(document):
    with get_client() as client:
        document_index = Index(name=document.Index.name, using=client)
        document_index.document(document)
        document_index.analyzer(ngram_analyzer)

        if document_index.exists():
            document_index.close(using=client)
            document_index.save(using=client)
            document_index.open(using=client)
        else:
            document_index.save(using=client)
