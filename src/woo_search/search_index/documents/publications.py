from elasticsearch_dsl import Date, Document as ES_Document, Text


class Document(ES_Document):
    uuid = Text()
    publicatie = Text()
    publisher = Text()
    identifier = Text()
    officiele_titel = Text()
    verkorte_titel = Text()
    omschrijving = Text()
    creatiedatum = Date()
    registratiedatum = Date()
    laatst_gewijzigd_datum = Date()

    class Index:
        name = "document"
