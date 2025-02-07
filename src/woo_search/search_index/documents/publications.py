from elasticsearch_dsl import Date, Document as ES_Document, Text


class Document(ES_Document):
    uuid = Text(required=True)
    publicatie = Text(required=True)
    publisher = Text(required=True)
    identifier = Text()
    officiele_titel = Text(required=True)
    verkorte_titel = Text()
    omschrijving = Text()
    creatiedatum = Date(required=True)
    registratiedatum = Date(required=True)
    laatst_gewijzigd_datum = Date(required=True)

    class Index:
        name = "document"
