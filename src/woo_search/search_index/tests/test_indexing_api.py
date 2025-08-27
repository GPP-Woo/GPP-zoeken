from datetime import UTC, date, datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

from django.test import override_settings
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.test import APITestCase

from woo_search.api.tests.mixin import APIKeyUnAuthorizedMixin, TokenAuthMixin
from woo_search.search_index.client import get_client
from woo_search.utils.tests.vcr import VCRMixin

from ..index import Document, Publication, Topic
from .base import ElasticSearchAPITestCase
from .factories import IndexDocumentFactory, IndexPublicationFactory


class DocumentAuthorizationApiTest(APIKeyUnAuthorizedMixin, APITestCase):
    def test_api_with_wrong_credentials_blocks_access(self):
        with self.subTest("create endpoint"):
            url = reverse("api:document-list")

            self.assertWrongApiKeyProhibitsPostEndpointAccess(url)

        with self.subTest("delete endpoint"):
            detail_url = reverse("api:document-detail", kwargs={"uuid": uuid4()})

            self.assertWrongApiKeyProhibitsDeleteEndpointAccess(detail_url)


class DocumentAPITests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("api:document-list")

    @patch("woo_search.search_index.api.viewsets.index_document.delay")
    def test_document_api_happy_flow(self, patched_index_document):
        data = {
            "uuid": "0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "informatieCategorieen": [
                {"uuid": "cd26d21a-8c49-4dff-ae82-20f4e28dfbaf", "naam": "WOO"}
            ],
            "onderwerpen": [],
            "identifiers": ["kenmerk"],
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
            "gepubliceerdOp": "2025-02-04T00:00:00.000000+00:00",
            "laatstGewijzigdDatum": "2025-02-04T00:00:00.000000+00:00",
            "downloadUrl": "https://www.example.com/downloads/1",
            "fileSize": 3124,
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Exact same data but the keys are snake_case which matches the unprocessed
        # response.data from the serializer
        snake_case_data = {
            "uuid": "0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "informatie_categorieen": [
                {"uuid": "cd26d21a-8c49-4dff-ae82-20f4e28dfbaf", "naam": "WOO"}
            ],
            "onderwerpen": [],
            "identifiers": ["kenmerk"],
            "publisher": {
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            "officiele_titel": "Een erg belangrijk bestand.",
            "verkorte_titel": "Een bestand.",
            "omschrijving": "bla bla bla bla.",
            "creatiedatum": date(2025, 2, 4),
            "registratiedatum": datetime(2025, 2, 4, 0, 0, 0, tzinfo=UTC),
            "gepubliceerd_op": datetime(2025, 2, 4, 0, 0, 0, tzinfo=UTC),
            "laatst_gewijzigd_datum": datetime(2025, 2, 4, 0, 0, 0, tzinfo=UTC),
            "download_url": "https://www.example.com/downloads/1",
            "file_size": 3124,
        }

        patched_index_document.assert_called_once_with(**snake_case_data)

    def test_document_api_with_download_url_and_without_filesize_result_in_error(
        self,
    ):
        data = {
            "uuid": "0d4e984f-495e-4219-8858-04af18b197f2",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "informatieCategorieen": [
                {"uuid": "cd26d21a-8c49-4dff-ae82-20f4e28dfbaf", "naam": "WOO"}
            ],
            "onderwerpen": [],
            "identifiers": [],
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
            "gepubliceerdOp": "2025-02-04T00:00:00.000000+00:00",
            "laatstGewijzigdDatum": "2025-02-04T00:00:00.000000+00:00",
            "downloadUrl": "https://www.example.com/downloads/1",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = response.json()
        self.assertEqual(
            data["fileSize"][0], _("Field is required when using `downloadUrl`.")
        )

    @patch("woo_search.search_index.api.viewsets.index_document.delay")
    def test_document_api_with_errors_does_not_call_index_document_celery_task(
        self, patched_index_document
    ):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        patched_index_document.assert_not_called()


class RemoveDocumentFromIndexAPITests(TokenAuthMixin, APITestCase):
    @patch("woo_search.search_index.api.viewsets.remove_document_from_index.delay")
    def test_remove_document_from_index(self, patched_remove_document):
        patched_remove_document.return_value.id = "my-task-id"
        document_id = str(uuid4())
        endpoint = reverse("api:document-detail", kwargs={"uuid": document_id})

        response = self.client.delete(endpoint)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.json()["taskId"], "my-task-id")
        patched_remove_document.assert_called_once_with(uuid=document_id)


class DocumentApiE2ETest(TokenAuthMixin, VCRMixin, ElasticSearchAPITestCase):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_document_creation_happy_flow(self):
        url = reverse_lazy("api:document-list")
        data = IndexDocumentFactory.build(
            uuid="0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            identifiers=["kenmerk"],
        )

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # verify that it's indexed
        with get_client() as client:
            doc = Document.get(using=client, id="0c5730c7-17ed-42a7-bc3b-5ee527ef3326")

        self.assertIsNotNone(doc, "Expected doc to be indexed")

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_document_creation_without_optional_published_date(self):
        url = reverse_lazy("api:document-list")
        data = {
            "uuid": "0d4e984f-495e-4219-8858-04af18b197f2",
            "publicatie": "e28fba05-14b3-4d9f-94c1-de95b60cc5b3",
            "informatieCategorieen": [
                {"uuid": "cd26d21a-8c49-4dff-ae82-20f4e28dfbaf", "naam": "WOO"}
            ],
            "onderwerpen": [],
            "identifiers": ["kenmerk"],
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
            "downloadUrl": "https://www.example.com/downloads/1",
            "fileSize": 3124,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # verify that it's indexed
        with get_client() as client:
            doc = Document.get(using=client, id="0d4e984f-495e-4219-8858-04af18b197f2")

        self.assertIsNotNone(doc, "Expected doc to be indexed")

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_document_deprecated_identifier_field_populates_identifiers(self):
        url = reverse_lazy("api:document-list")
        data = IndexDocumentFactory.build(
            uuid="0c5730c7-17ed-42a7-bc3b-5ee527ef3326",
            identifier="kenmerk",
            identifiers=[],
        )

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # verify that it's indexed
        with get_client() as client:
            doc = Document.get(using=client, id="0c5730c7-17ed-42a7-bc3b-5ee527ef3326")

        assert doc is not None, "Expected doc to be indexed"
        self.assertEqual(doc.identifiers, ["kenmerk"])


class PublicationAuthorizationApiTest(APIKeyUnAuthorizedMixin, APITestCase):
    def test_api_with_wrong_credentials_blocks_access(self):
        with self.subTest("create endpoint"):
            url = reverse_lazy("api:publication-list")

            self.assertWrongApiKeyProhibitsPostEndpointAccess(url)

        with self.subTest("delete endpoint"):
            detail_url = reverse("api:publication-detail", kwargs={"uuid": uuid4()})

            self.assertWrongApiKeyProhibitsDeleteEndpointAccess(detail_url)


class PublicationAPITests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("api:publication-list")

    @patch("woo_search.search_index.api.viewsets.index_publication.delay")
    def test_publication_api_happy_flow(self, patched_index_document):
        data = {
            "uuid": "a74cc327-9e22-400c-b79e-82e61c082c99",
            "publisher": {
                "uuid": "febfb068-7992-4973-9e96-1b4cfc056605",
                "naam": "Utrecht",
            },
            "informatieCategorieen": [
                {"uuid": "cd26d21a-8c49-4dff-ae82-20f4e28dfbaf", "naam": "WOO"}
            ],
            "identifiers": [],
            "onderwerpen": [
                {
                    "uuid": "d8de905b-59c2-464d-b190-494a9134fb75",
                    "officiele_titel": "GPP",
                }
            ],
            "officiele_titel": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            "verkorte_titel": "Donec finibus non tortor quis sollicitudin.",
            "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
            "registratiedatum": "2025-02-10T15:00:00.000000+00:00",
            "gepubliceerdOp": "2025-02-10T15:00:00.000000+00:00",
            "laatstGewijzigdDatum": "2025-02-15T15:00:00.000000+00:00",
            "datumBeginGeldigheid": "2025-02-15T15:00:00.000000+00:00",
            "datumEindeGeldigheid": "2025-02-15T15:00:00.000000+00:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Exact same data but the keys are snake_case which matches the unprocessed
        # response.data from the serializer
        snake_case_data = {
            "uuid": "a74cc327-9e22-400c-b79e-82e61c082c99",
            "publisher": {
                "uuid": "febfb068-7992-4973-9e96-1b4cfc056605",
                "naam": "Utrecht",
            },
            "informatie_categorieen": [
                {"uuid": "cd26d21a-8c49-4dff-ae82-20f4e28dfbaf", "naam": "WOO"}
            ],
            "identifiers": [],
            "onderwerpen": [
                {
                    "uuid": "d8de905b-59c2-464d-b190-494a9134fb75",
                    "officiele_titel": "GPP",
                }
            ],
            "officiele_titel": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            "verkorte_titel": "Donec finibus non tortor quis sollicitudin.",
            "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
            "registratiedatum": datetime(2025, 2, 10, 15, 0, 0, tzinfo=UTC),
            "gepubliceerd_op": datetime(2025, 2, 10, 15, 0, 0, tzinfo=UTC),
            "laatst_gewijzigd_datum": datetime(2025, 2, 15, 15, 0, 0, tzinfo=UTC),
            "datum_begin_geldigheid": datetime(2025, 2, 15, 15, 0, 0, tzinfo=UTC),
            "datum_einde_geldigheid": datetime(2025, 2, 15, 15, 0, 0, tzinfo=UTC),
        }

        patched_index_document.assert_called_once_with(**snake_case_data)

    @patch("woo_search.search_index.api.viewsets.index_publication.delay")
    def test_publication_api_happy_flow_without_optional_dates(
        self, patched_index_document
    ):
        data = {
            "uuid": "a74cc327-9e22-400c-b79e-82e61c082c99",
            "publisher": {
                "uuid": "febfb068-7992-4973-9e96-1b4cfc056605",
                "naam": "Utrecht",
            },
            "informatieCategorieen": [
                {"uuid": "cd26d21a-8c49-4dff-ae82-20f4e28dfbaf", "naam": "WOO"}
            ],
            "identifiers": [],
            "onderwerpen": [
                {
                    "uuid": "d8de905b-59c2-464d-b190-494a9134fb75",
                    "officiele_titel": "GPP",
                }
            ],
            "officiele_titel": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            "verkorte_titel": "Donec finibus non tortor quis sollicitudin.",
            "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
            "registratiedatum": "2025-02-10T15:00:00.000000+00:00",
            "gepubliceerdOp": None,
            "laatstGewijzigdDatum": "2025-02-15T15:00:00.000000+00:00",
            "datumBeginGeldigheid": None,
            "datumEindeGeldigheid": None,
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Exact same data but the keys are snake_case which matches the unprocessed
        # response.data from the serializer
        snake_case_data = {
            "uuid": "a74cc327-9e22-400c-b79e-82e61c082c99",
            "publisher": {
                "uuid": "febfb068-7992-4973-9e96-1b4cfc056605",
                "naam": "Utrecht",
            },
            "informatie_categorieen": [
                {"uuid": "cd26d21a-8c49-4dff-ae82-20f4e28dfbaf", "naam": "WOO"}
            ],
            "identifiers": [],
            "onderwerpen": [
                {
                    "uuid": "d8de905b-59c2-464d-b190-494a9134fb75",
                    "officiele_titel": "GPP",
                }
            ],
            "officiele_titel": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            "verkorte_titel": "Donec finibus non tortor quis sollicitudin.",
            "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
            "registratiedatum": datetime(2025, 2, 10, 15, 0, 0, tzinfo=UTC),
            "gepubliceerd_op": None,
            "laatst_gewijzigd_datum": datetime(2025, 2, 15, 15, 0, 0, tzinfo=UTC),
            "datum_begin_geldigheid": None,
            "datum_einde_geldigheid": None,
        }

        patched_index_document.assert_called_once_with(**snake_case_data)

    @patch("woo_search.search_index.api.viewsets.index_publication.delay")
    def test_publication_api_with_errors_does_not_call_index_document_celery_task(
        self, patched_index_document
    ):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        patched_index_document.assert_not_called()


class RemovePublicationFromIndexAPITests(TokenAuthMixin, APITestCase):
    @patch("woo_search.search_index.api.viewsets.remove_publication_from_index.delay")
    def test_remove_publication_from_index(self, patched_remove_publication):
        patched_remove_publication.return_value.id = "my-task-id"
        publication_id = str(uuid4())
        endpoint = reverse("api:publication-detail", kwargs={"uuid": publication_id})

        response = self.client.delete(endpoint)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.json()["taskId"], "my-task-id")
        patched_remove_publication.assert_called_once_with(uuid=publication_id)


class PublicationApiE2ETest(TokenAuthMixin, VCRMixin, ElasticSearchAPITestCase):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_publication_creation_happy_flow(self):
        url = reverse_lazy("api:publication-list")
        data = IndexPublicationFactory.build(
            uuid="825d61d1-2bdd-4e11-8166-796e96a0bc07",
            identifiers=["kenmerk"],
        )

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # verify that it's indexed
        with get_client() as client:
            doc = Publication.get(
                using=client, id="825d61d1-2bdd-4e11-8166-796e96a0bc07"
            )

        self.assertIsNotNone(doc, "Expected doc to be indexed")

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_publication_creation_without_optional_date_fields(self):
        url = reverse_lazy("api:publication-list")
        data = {
            "uuid": "a74cc327-9e22-400c-b79e-82e61c082c99",
            "publisher": {
                "uuid": "febfb068-7992-4973-9e96-1b4cfc056605",
                "naam": "Utrecht",
            },
            "informatieCategorieen": [
                {"uuid": "cd26d21a-8c49-4dff-ae82-20f4e28dfbaf", "naam": "WOO"}
            ],
            "identifiers": [],
            "onderwerpen": [
                {
                    "uuid": "d8de905b-59c2-464d-b190-494a9134fb75",
                    "officiele_titel": "GPP",
                }
            ],
            "officiele_titel": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            "verkorte_titel": "Donec finibus non tortor quis sollicitudin.",
            "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
            "registratiedatum": "2025-02-10T15:00:00.000000+00:00",
            "laatstGewijzigdDatum": "2025-02-15T15:00:00.000000+00:00",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # verify that it's indexed
        with get_client() as client:
            doc = Publication.get(
                using=client, id="a74cc327-9e22-400c-b79e-82e61c082c99"
            )

        self.assertIsNotNone(doc, "Expected doc to be indexed")


class TopicAuthorizationApiTest(APIKeyUnAuthorizedMixin, APITestCase):
    def test_api_with_wrong_credentials_blocks_access(self):
        with self.subTest("create endpoint"):
            url = reverse("api:topic-list")

            self.assertWrongApiKeyProhibitsPostEndpointAccess(url)

        with self.subTest("delete endpoint"):
            detail_url = reverse("api:topic-detail", kwargs={"uuid": uuid4()})

            self.assertWrongApiKeyProhibitsDeleteEndpointAccess(detail_url)


class TopicAPITests(TokenAuthMixin, APITestCase):
    url = reverse_lazy("api:topic-list")

    @patch("woo_search.search_index.api.viewsets.index_topic.delay")
    def test_topic_api_happy_flow(self, patched_index_topic_delay: MagicMock):
        data = {
            "uuid": "a74cc327-9e22-400c-b79e-82e61c082c99",
            "officieleTitel": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
            "registratiedatum": "2025-02-10T15:00:00.000000+00:00",
            "laatstGewijzigdDatum": "2025-02-15T15:00:00.000000+00:00",
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Exact same data but the keys are snake_case which matches the unprocessed
        # response.data from the serializer
        snake_case_data = {
            "uuid": "a74cc327-9e22-400c-b79e-82e61c082c99",
            "officiele_titel": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
            "registratiedatum": datetime(2025, 2, 10, 15, 0, 0, tzinfo=UTC),
            "laatst_gewijzigd_datum": datetime(2025, 2, 15, 15, 0, 0, tzinfo=UTC),
        }

        patched_index_topic_delay.assert_called_once_with(**snake_case_data)

    @patch("woo_search.search_index.api.viewsets.index_topic.delay")
    def test_topic_api_with_errors_does_not_call_index_document_celery_task(
        self, patched_index_topic_delay: MagicMock
    ):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        patched_index_topic_delay.assert_not_called()


class RemoveTopicFromIndexAPITests(TokenAuthMixin, APITestCase):
    @patch("woo_search.search_index.api.viewsets.remove_topic_from_index.delay")
    def test_remove_topic_from_index(self, patched_remove_topic_mock: MagicMock):
        patched_remove_topic_mock.return_value.id = "my-task-id"
        topic_id = str(uuid4())
        endpoint = reverse("api:topic-detail", kwargs={"uuid": topic_id})

        response = self.client.delete(endpoint)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.json()["taskId"], "my-task-id")
        patched_remove_topic_mock.assert_called_once_with(uuid=topic_id)


class TopicApiE2ETest(TokenAuthMixin, VCRMixin, ElasticSearchAPITestCase):
    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_topic_creation_happy_flow(self):
        url = reverse_lazy("api:topic-list")
        data = {
            "uuid": "71f60b40-c426-4ec2-a2af-438862b27ede",
            "officieleTitel": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
            "registratiedatum": datetime(2025, 2, 15, 15, 0, 0, tzinfo=UTC),
            "laatstGewijzigdDatum": datetime(2025, 2, 15, 15, 0, 0, tzinfo=UTC),
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        # verify that it's indexed
        with get_client() as client:
            doc = Topic.get(using=client, id="71f60b40-c426-4ec2-a2af-438862b27ede")

        assert doc is not None, "Expected doc to be indexed"
        # Test that the indexed gepubliceerd_op is the same as registratiedatum
        self.assertEqual(
            doc["gepubliceerd_op"], datetime(2025, 2, 15, 15, 0, 0, tzinfo=UTC)
        )
