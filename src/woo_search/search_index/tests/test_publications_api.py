from datetime import date, datetime, timezone
from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from woo_search.api.tests.mixin import APIKeyUnAuthorizedMixin, TokenAuthMixin
from woo_search.search_index.client import get_client
from woo_search.utils.tests.vcr import VCRMixin

from ..documents import Document
from .base import ElasticSearchAPITestCase


class DocumentApiTest(APIKeyUnAuthorizedMixin, APITestCase):
    def test_api_with_wrong_credentials_blocks_access(self):
        url = reverse("api:document-list")

        self.assertWrongApiKeyProhibitsPostEndpointAccess(url)


class DocumentAPITest(TokenAuthMixin, APITestCase):
    url = reverse("api:document-list")

    @patch("woo_search.search_index.tasks.publications.index_document.delay")
    def test_document_api_happy_flow(self, patched_index_document):
        data = {
            "uuid": "0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "publisher": {
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            "identifier": "https://example.com/b36519a5-64d9-4316-a042-3ac5406f8f61",
            "officieleTitel": "Een erg belangrijk bestand.",
            "verkorteTitel": "Een bestand.",
            "omschrijving": "bla bla bla bla.",
            "creatiedatum": "2025-02-04",
            "registratiedatum": "2025-02-04T00:00:00.000000+00:00",
            "laatstGewijzigdDatum": "2025-02-04T00:00:00.000000+00:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Exact same data but the keys are snake_case which matches the unprocessed response.data from the serializer
        snake_case_data = {
            "uuid": "0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "publisher": {
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            "identifier": "https://example.com/b36519a5-64d9-4316-a042-3ac5406f8f61",
            "officiele_titel": "Een erg belangrijk bestand.",
            "verkorte_titel": "Een bestand.",
            "omschrijving": "bla bla bla bla.",
            "creatiedatum": date(2025, 2, 4),
            "registratiedatum": datetime(2025, 2, 4, 0, 0, 0, tzinfo=timezone.utc),
            "laatst_gewijzigd_datum": datetime(
                2025, 2, 4, 0, 0, 0, tzinfo=timezone.utc
            ),
        }

        patched_index_document.assert_called_once_with(**snake_case_data)

    @patch("woo_search.search_index.tasks.publications.index_document.delay")
    def test_document_api_with_errors_does_not_call_index_document_celery_task(
        self, patched_index_document
    ):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        patched_index_document.assert_not_called()


class DocumentApiE2ETest(TokenAuthMixin, VCRMixin, ElasticSearchAPITestCase):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_document_creation_happy_flow(self):
        url = reverse("api:document-list")
        data = {
            "uuid": "0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "publisher": {
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            "identifier": "https://example.com/b36519a5-64d9-4316-a042-3ac5406f8f61",
            "officieleTitel": "Een erg belangrijk bestand.",
            "verkorteTitel": "Een bestand.",
            "omschrijving": "bla bla bla bla.",
            "creatiedatum": "2025-02-04",
            "registratiedatum": "2025-02-04T15:42:53.646693+01:00",
            "laatstGewijzigdDatum": "2025-02-04T15:42:53.646700+01:00",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # verify that it's indexed
        with get_client() as client:
            doc = Document.get(using=client, id="0c5730c7-17ed-42a7-bc3b-5ee527ef3326")

        self.assertIsNotNone(doc, "Expected doc to be indexed")
