import uuid
from unittest import TestCase

from elasticsearch_dsl import connections

from woo_search.utils.tests.vcr import VCRMixin

from ..tasks import index_document


class TasksTestCase(VCRMixin, TestCase):
    def test_index_document_happy_flow(self):
        data = {
            "uuid": uuid.UUID("0095704d-4216-4de3-83d2-20dba551b0dc").hex,
            "publicatie": uuid.UUID("d481bea6-335b-4d90-9b27-ac49f7196633").hex,
            "publisher": uuid.UUID("f8b2b355-1d6e-4c1a-ba18-565f422997da").hex,
            "identifier": "https://www.example.com/1",
            "officiele_titel": "Een test document",
            "verkorte_titel": "Een document",
            "omschrijving": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "creatiedatum": "2026-01-01",
            "registratiedatum": "2026-01-05T12:00:00.000000+00:00",
            "laatst_gewijzigd_datum": "2026-01-05T12:00:00.000000+00:00",
        }

        # Run index document as a function instead of a task.
        index_document(data)

        search_created_document_index = connections.get_connection().search(
            index="document",
            body={
                "query": {
                    "bool": {
                        "must": [{"match": {"officiele_titel": "Een test document"}}]
                    }
                }
            },
        )

        # Transformed input data
        es_data = {
            "uuid": "0095704d-4216-4de3-83d2-20dba551b0dc",
            "publicatie": "d481bea6-335b-4d90-9b27-ac49f7196633",
            "publisher": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
            "identifier": "https://www.example.com/1",
            "officiele_titel": "Een test document",
            "verkorte_titel": "Een document",
            "omschrijving": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "creatiedatum": "2026-01-01T00:00:00",
            "registratiedatum": "2026-01-05T12:00:00+00:00",
            "laatst_gewijzigd_datum": "2026-01-05T12:00:00+00:00",
        }

        # Test if there only is 1 single hit
        self.assertEqual(search_created_document_index["hits"]["total"]["value"], 1)
        # Test if the data matches the stored value
        self.assertEqual(
            search_created_document_index["hits"]["hits"][0]["_source"], es_data
        )
