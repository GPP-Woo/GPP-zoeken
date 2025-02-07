import uuid
from unittest import TestCase

from woo_search.typing import ESSource
from woo_search.utils.tests.vcr import VCRMixin

from ...utils.tests.es_tools import retry
from ..client import get_client
from ..tasks import save_document


class DocumentTaskTest(VCRMixin, TestCase):
    def test_index_document_happy_flow(self):
        data = {
            "uuid": uuid.UUID("0095704d-4216-4de3-83d2-20dba551b0dc"),
            "publicatie": uuid.UUID("d481bea6-335b-4d90-9b27-ac49f7196633"),
            "publisher": uuid.UUID("f8b2b355-1d6e-4c1a-ba18-565f422997da"),
            "identifier": "https://www.example.com/1",
            "officiele_titel": "Een test document",
            "verkorte_titel": "Een document",
            "omschrijving": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "creatiedatum": "2026-01-01",
            "registratiedatum": "2026-01-05T12:00:00.000000+00:00",
            "laatst_gewijzigd_datum": "2026-01-05T12:00:00.000000+00:00",
        }

        # Run index document as a function instead of a task.
        save_document(data)

        # Transformed input data
        es_expected_data = {
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

        def retrieve_doc_data() -> ESSource:
            es_response = get_client().search(
                index="document",
                body={
                    "query": {
                        "match": {
                            "uuid": "0095704d-4216-4de3-83d2-20dba551b0dc",
                        },
                    },
                },
            )

            if es_response["hits"]["total"]["value"] >= 1:
                return es_response["hits"]["hits"][0]["_source"]

            return None

        data = retry(retrieve_doc_data)

        # Test if the data matches the stored value
        self.assertEqual(data, es_expected_data)
