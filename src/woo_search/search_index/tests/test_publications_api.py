from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from woo_search.search_index.client import get_client
from woo_search.typing import ESSource
from woo_search.utils.tests.es_tools import retry
from woo_search.utils.tests.vcr import VCRMixin


class PublicationsAPITest(APITestCase):
    url = reverse("api:documents-list")

    @patch("woo_search.search_index.tasks.publications.save_document.delay")
    def test_document_api_happy_flow(self, patched_index_document):
        data = {
            "uuid": "0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "publisher": "5af7ceb9-de9b-4646-8c6d-c65151c76825",
            "identifier": "https://example.com/b36519a5-64d9-4316-a042-3ac5406f8f61",
            "officieleTitel": "Een erg belangrijk bestand.",
            "verkorteTitel": "Een bestand.",
            "omschrijving": "bla bla bla bla.",
            "creatiedatum": "2025-02-04",
            "registratiedatum": "2025-02-04T15:42:53.646693+01:00",
            "laatstGewijzigdDatum": "2025-02-04T15:42:53.646700+01:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), data)

        # Exact same data but the keys are snake_case which matches the unprocessed response.data from the serializer
        snake_case_data = {
            "uuid": "0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "publisher": "5af7ceb9-de9b-4646-8c6d-c65151c76825",
            "identifier": "https://example.com/b36519a5-64d9-4316-a042-3ac5406f8f61",
            "officiele_titel": "Een erg belangrijk bestand.",
            "verkorte_titel": "Een bestand.",
            "omschrijving": "bla bla bla bla.",
            "creatiedatum": "2025-02-04",
            "registratiedatum": "2025-02-04T15:42:53.646693+01:00",
            "laatst_gewijzigd_datum": "2025-02-04T15:42:53.646700+01:00",
        }

        patched_index_document.assert_called_once_with(snake_case_data)

    @patch("woo_search.search_index.tasks.publications.save_document.delay")
    def test_document_api_with_errors_does_not_call_index_document_celery_task(
        self, patched_index_document
    ):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        patched_index_document.assert_not_called()


class DocumentApiE2ETest(VCRMixin, APITestCase):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_document_creation_happy_flow(self):
        url = reverse("api:documents-list")
        data = {
            "uuid": "0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "publisher": "5af7ceb9-de9b-4646-8c6d-c65151c76825",
            "identifier": "https://example.com/b36519a5-64d9-4316-a042-3ac5406f8f61",
            "officieleTitel": "Een erg belangrijk bestand.",
            "verkorteTitel": "Een bestand.",
            "omschrijving": "bla bla bla bla.",
            "creatiedatum": "2025-02-04",
            "registratiedatum": "2025-02-04T15:42:53.646693+01:00",
            "laatstGewijzigdDatum": "2025-02-04T15:42:53.646700+01:00",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), data)

        # Transformed input data, changed keys to snake_case and added time to creation data field
        es_expected_data = {
            "uuid": "0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "publisher": "5af7ceb9-de9b-4646-8c6d-c65151c76825",
            "identifier": "https://example.com/b36519a5-64d9-4316-a042-3ac5406f8f61",
            "officiele_titel": "Een erg belangrijk bestand.",
            "verkorte_titel": "Een bestand.",
            "omschrijving": "bla bla bla bla.",
            "creatiedatum": "2025-02-04T00:00:00",
            "registratiedatum": "2025-02-04T15:42:53.646693+01:00",
            "laatst_gewijzigd_datum": "2025-02-04T15:42:53.646700+01:00",
        }

        def retrieve_doc_data() -> ESSource:
            es_response = get_client().search(
                index="document",
                body={
                    "query": {
                        "match": {
                            "uuid": "0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
                        },
                    },
                },
            )

            if es_response["hits"]["total"]["value"] >= 1:
                return es_response["hits"]["hits"][0]["_source"]

            return None

        data = retry(retrieve_doc_data, max_wait_s=2)

        # Test if the data matches the stored value
        self.assertEqual(data, es_expected_data)
