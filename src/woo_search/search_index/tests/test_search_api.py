from datetime import date, datetime, timezone

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from woo_search.api.tests.mixin import APIKeyUnAuthorizedMixin, TokenAuthMixin
from woo_search.utils.tests.vcr import VCRMixin

from ..tasks import index_document, index_publication
from .base import ElasticSearchAPITestCase
from .factories import IndexDocumentFactory, IndexPublicationFactory


class SearchApiAccessTest(APIKeyUnAuthorizedMixin, APITestCase):
    def test_api_with_wrong_credentials_blocks_access(self):
        url = reverse_lazy("api:search")

        self.assertWrongApiKeyProhibitsPostEndpointAccess(url)


class SearchApiTest(TokenAuthMixin, VCRMixin, ElasticSearchAPITestCase):
    url = reverse_lazy("api:search")
    maxDiff = None

    def test_no_body(self):
        index_publication(
            uuid="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "62da7e9d-2481-4d46-9c77-563b490126aa",
                "naam": "Utrecht",
            },
            informatie_categorieen=[
                {"uuid": "2ff3d47c-7945-4267-b3b2-e63aca280b8d", "naam": "WOO"}
            ],
            officiele_titel="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            verkorte_titel="Donec finibus non tortor quis sollicitudin.",
            omschrijving="Nulla at nisi at enim eleifend facilisis at vitae velit.",
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="525747fd-7e58-4005-8efa-59bcf4403385",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="document1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 2)
        self.assertFalse(data["previous"])
        self.assertFalse(data["next"])
        # test if results have the same length as the count
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(
            data["results"][0],
            {
                "type": "document",
                "record": {
                    "uuid": "525747fd-7e58-4005-8efa-59bcf4403385",
                    "publicatie": "6dae9be7-4f93-4aad-b56a-10b683b16dcc",
                    "publisher": {
                        "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                        "naam": "Utrecht",
                    },
                    "identifier": "document1",
                    "officieleTitel": "A test document",
                    "verkorteTitel": "A document",
                    "omschrijving": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "creatiedatum": "2026-01-01",
                    "registratiedatum": "2026-01-05T13:00:00+01:00",
                    "laatstGewijzigdDatum": "2026-01-05T13:00:00+01:00",
                },
            },
        )
        self.assertEqual(
            data["results"][1],
            {
                "type": "publication",
                "record": {
                    "uuid": "6dae9be7-4f93-4aad-b56a-10b683b16dcc",
                    "publisher": {
                        "uuid": "62da7e9d-2481-4d46-9c77-563b490126aa",
                        "naam": "Utrecht",
                    },
                    "informatieCategorieen": [
                        {"uuid": "2ff3d47c-7945-4267-b3b2-e63aca280b8d", "naam": "WOO"}
                    ],
                    "officieleTitel": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "verkorteTitel": "Donec finibus non tortor quis sollicitudin.",
                    "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
                    "registratiedatum": "2026-01-05T13:00:00+01:00",
                    "laatstGewijzigdDatum": "2026-01-05T13:00:00+01:00",
                },
            },
        )

    def test_pagination_next_and_page_size(self):
        index_publication(
            uuid="1aa78d62-0cc7-4273-86b4-8c6bf4f28a98",
            publisher={
                "uuid": "62da7e9d-2481-4d46-9c77-563b490126aa",
                "naam": "Utrecht",
            },
            informatie_categorieen=[
                {"uuid": "2ff3d47c-7945-4267-b3b2-e63aca280b8d", "naam": "WOO"}
            ],
            officiele_titel="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            verkorte_titel="Donec finibus non tortor quis sollicitudin.",
            omschrijving="Nulla at nisi at enim eleifend facilisis at vitae velit.",
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="85a095ea-e1fa-438c-9e05-1862874f57a0",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="document1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        response = self.client.post(self.url, {"page": 1, "pageSize": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 2)
        self.assertFalse(data["previous"])
        self.assertTrue(data["next"])
        # test if results have the same length as the count
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["type"], "document")

    def test_pagination_previous(self):
        index_publication(
            uuid="80485d67-0b97-4ed5-8483-f2d03d012e19",
            publisher={
                "uuid": "62da7e9d-2481-4d46-9c77-563b490126aa",
                "naam": "Utrecht",
            },
            informatie_categorieen=[
                {"uuid": "2ff3d47c-7945-4267-b3b2-e63aca280b8d", "naam": "WOO"}
            ],
            officiele_titel="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            verkorte_titel="Donec finibus non tortor quis sollicitudin.",
            omschrijving="Nulla at nisi at enim eleifend facilisis at vitae velit.",
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="48981334-b480-4e7d-8c8d-925bbc67a969",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="document1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        response = self.client.post(self.url, {"page": 2, "pageSize": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 2)
        self.assertTrue(data["previous"])
        self.assertFalse(data["next"])
        # test if results have the same length as the count
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["type"], "publication")

    def test_sort_chronological(self):
        index_publication(
            uuid="0ce718e4-8fb5-42f1-a07e-cbf82a869efd",
            publisher={
                "uuid": "62da7e9d-2481-4d46-9c77-563b490126aa",
                "naam": "Utrecht",
            },
            informatie_categorieen=[
                {"uuid": "2ff3d47c-7945-4267-b3b2-e63aca280b8d", "naam": "WOO"}
            ],
            officiele_titel="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            verkorte_titel="Donec finibus non tortor quis sollicitudin.",
            omschrijving="Nulla at nisi at enim eleifend facilisis at vitae velit.",
            registratiedatum=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 2, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="3b3f4514-7d8b-4e31-83ca-fa9376ff6522",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="document1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        response = self.client.post(self.url, {"sort": "chronological"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 2)
        self.assertFalse(data["previous"])
        self.assertFalse(data["next"])
        # test if results have the same length as the count
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["type"], "document")
        self.assertEqual(data["results"][1]["type"], "publication")

    def test_result_type(self):
        index_publication(
            uuid="5fc73bff-3cc2-4619-90d7-74b3eb3e4101",
            publisher={
                "uuid": "62da7e9d-2481-4d46-9c77-563b490126aa",
                "naam": "Utrecht",
            },
            informatie_categorieen=[
                {"uuid": "2ff3d47c-7945-4267-b3b2-e63aca280b8d", "naam": "WOO"}
            ],
            officiele_titel="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            verkorte_titel="Donec finibus non tortor quis sollicitudin.",
            omschrijving="Nulla at nisi at enim eleifend facilisis at vitae velit.",
            registratiedatum=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 2, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="387d982b-d7c8-48e8-9665-2dbfb6f8688c",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="document1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        response = self.client.post(self.url, {"resultType": "document"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["type"], "document")

        with self.subTest("facets returned"):
            self.assertIn("facets", data)
            self.assertIn("resultTypes", data["facets"])
            result_types = data["facets"]["resultTypes"]
            self.assertEqual(
                result_types,
                [{"name": "document", "count": 1}],
            )

    def test_query(self):
        index_publication(
            uuid="50e32c44-515e-4c48-ae57-3aae82fc9cf1",
            publisher={
                "uuid": "62da7e9d-2481-4d46-9c77-563b490126aa",
                "naam": "Utrecht",
            },
            informatie_categorieen=[
                {"uuid": "2ff3d47c-7945-4267-b3b2-e63aca280b8d", "naam": "WOO"}
            ],
            officiele_titel="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            verkorte_titel="Donec finibus non tortor quis sollicitudin.",
            omschrijving="Nulla at nisi at enim eleifend facilisis at vitae velit.",
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="6dd95a10-cc97-4f19-b7e4-2c85358acb98",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="document1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        response = self.client.post(self.url, {"query": "document1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertFalse(data["previous"])
        self.assertFalse(data["next"])
        # test if results have the same length as the count
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["type"], "document")

    def test_query_field_boosts(self):
        index_document(
            uuid="3916925a-4260-4505-bfbb-0942113efd49",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="document1",
            officiele_titel="titel",
            verkorte_titel="snowflake",
            omschrijving="omschrijving",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="d49bc304-01a1-4eda-a914-a8dda5c901e2",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="snowflake",
            officiele_titel="titel",
            verkorte_titel="verkorte titel",
            omschrijving="omschrijving",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="bdcc4cea-b186-425e-8dcd-9fecb6818563",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="document3",
            officiele_titel="titel",
            verkorte_titel="verkorte titel",
            omschrijving="snowflake",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="7eade718-bccb-4876-9f00-a095beebc360",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="document4",
            officiele_titel="snowflake",
            verkorte_titel="verkorte titel",
            omschrijving="omschrijving",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        response = self.client.post(self.url, {"query": "snowflake"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 4)
        # see if the field priority goes as following:
        # - identifier
        # - officiele_titel
        # - verkorte_titel
        # - omschrijving
        self.assertEqual(
            data["results"][0]["record"]["uuid"], "d49bc304-01a1-4eda-a914-a8dda5c901e2"
        )
        self.assertEqual(
            data["results"][1]["record"]["uuid"], "7eade718-bccb-4876-9f00-a095beebc360"
        )
        self.assertEqual(
            data["results"][2]["record"]["uuid"], "3916925a-4260-4505-bfbb-0942113efd49"
        )
        self.assertEqual(
            data["results"][3]["record"]["uuid"], "bdcc4cea-b186-425e-8dcd-9fecb6818563"
        )

    def test_filter_on_registration_date(self):
        doc1 = IndexDocumentFactory.build(
            uuid="6aac4fb2-d532-490b-bd6b-87b0257c0236",
            registratiedatum=datetime(2024, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
        )
        doc2 = IndexDocumentFactory.build(
            uuid="62fceb92-98bd-475c-b184-49ee8a274787",
            registratiedatum=datetime(2022, 12, 10, 18, 0, 0, tzinfo=timezone.utc),
        )
        doc3 = IndexDocumentFactory.build(
            uuid="ef1dead2-e0f8-45be-acf7-3583adc14906",
            registratiedatum=datetime(2025, 1, 14, 21, 12, 0, tzinfo=timezone.utc),
        )
        index_document(**doc1)
        index_document(**doc2)
        index_document(**doc3)

        with self.subTest(
            registratiedatum_vanaf="2024-01-01T00:00:00+01:00",
            registratiedatum_tot=None,
        ):
            response = self.client.post(
                self.url, {"registratiedatum_vanaf": "2024-01-01T00:00:00+01:00"}
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 2)
            expected_ids = {
                "6aac4fb2-d532-490b-bd6b-87b0257c0236",
                "ef1dead2-e0f8-45be-acf7-3583adc14906",
            }
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)

        with self.subTest(
            registratiedatum_vanaf=None,
            registratiedatum_tot="2022-12-31T23:59:59.999999+01:00",
        ):
            response = self.client.post(
                self.url, {"registratiedatum_tot": "2022-12-31T23:59:59.999999+01:00"}
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 1)
            expected_ids = {"62fceb92-98bd-475c-b184-49ee8a274787"}
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)

        with self.subTest(
            registratiedatum_vanaf="2024-01-01T00:00:00+01:00",
            registratiedatum_tot="2024-12-31T23:59:59.999999+01:00",
        ):
            response = self.client.post(
                self.url,
                {
                    "registratiedatum_vanaf": "2024-01-01T00:00:00+01:00",
                    "registratiedatum_tot": "2024-12-31T23:59:59.999999+01:00",
                },
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 1)
            expected_ids = {"6aac4fb2-d532-490b-bd6b-87b0257c0236"}
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)

    def test_filter_on_registration_date_both_indexes(self):
        pub1 = IndexPublicationFactory.build(
            uuid="b38065ee-322e-46c7-ae64-c47112a4b408",
            registratiedatum=datetime(2024, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
        )
        pub2 = IndexPublicationFactory.build(
            uuid="de225c2e-2700-4fee-a6ea-efa276db42d4",
            registratiedatum=datetime(2022, 12, 10, 18, 0, 0, tzinfo=timezone.utc),
        )
        doc1 = IndexDocumentFactory.build(
            uuid="6aac4fb2-d532-490b-bd6b-87b0257c0236",
            registratiedatum=datetime(2024, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
        )
        doc2 = IndexDocumentFactory.build(
            uuid="62fceb92-98bd-475c-b184-49ee8a274787",
            registratiedatum=datetime(2022, 12, 10, 18, 0, 0, tzinfo=timezone.utc),
        )
        index_publication(**pub1)
        index_publication(**pub2)
        index_document(**doc1)
        index_document(**doc2)

        response = self.client.post(
            self.url,
            {
                "registratiedatum_vanaf": "2024-01-01T00:00:00+01:00",
                "registratiedatum_tot": "2024-12-31T23:59:59.999999+01:00",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 2)
        expected_ids = {
            "b38065ee-322e-46c7-ae64-c47112a4b408",
            "6aac4fb2-d532-490b-bd6b-87b0257c0236",
        }
        ids = set(result["record"]["uuid"] for result in data["results"])
        self.assertEqual(ids, expected_ids)

    def test_filter_on_last_modified_date(self):
        doc1 = IndexDocumentFactory.build(
            uuid="6aac4fb2-d532-490b-bd6b-87b0257c0236",
            laatst_gewijzigd_datum=datetime(2024, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
        )
        doc2 = IndexDocumentFactory.build(
            uuid="62fceb92-98bd-475c-b184-49ee8a274787",
            laatst_gewijzigd_datum=datetime(
                2022, 12, 10, 18, 0, 0, tzinfo=timezone.utc
            ),
        )
        doc3 = IndexDocumentFactory.build(
            uuid="ef1dead2-e0f8-45be-acf7-3583adc14906",
            laatst_gewijzigd_datum=datetime(
                2025, 1, 14, 21, 12, 0, tzinfo=timezone.utc
            ),
        )
        index_document(**doc1)
        index_document(**doc2)
        index_document(**doc3)

        with self.subTest(
            laatst_gewijzigd_datum_vanaf="2024-01-01T00:00:00+01:00",
            laatst_gewijzigd_datum_tot=None,
        ):
            response = self.client.post(
                self.url, {"laatst_gewijzigd_datum_vanaf": "2024-01-01T00:00:00+01:00"}
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 2)
            expected_ids = {
                "6aac4fb2-d532-490b-bd6b-87b0257c0236",
                "ef1dead2-e0f8-45be-acf7-3583adc14906",
            }
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)

        with self.subTest(
            laatst_gewijzigd_datum_vanaf=None,
            laatst_gewijzigd_datum_tot="2022-12-31T23:59:59.999999+01:00",
        ):
            response = self.client.post(
                self.url,
                {"laatst_gewijzigd_datum_tot": "2022-12-31T23:59:59.999999+01:00"},
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 1)
            expected_ids = {"62fceb92-98bd-475c-b184-49ee8a274787"}
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)

        with self.subTest(
            laatst_gewijzigd_datum_vanaf="2024-01-01T00:00:00+01:00",
            laatst_gewijzigd_datum_tot="2024-12-31T23:59:59.999999+01:00",
        ):
            response = self.client.post(
                self.url,
                {
                    "laatst_gewijzigd_datum_vanaf": "2024-01-01T00:00:00+01:00",
                    "laatst_gewijzigd_datum_tot": "2024-12-31T23:59:59.999999+01:00",
                },
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 1)
            expected_ids = {"6aac4fb2-d532-490b-bd6b-87b0257c0236"}
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)

    def test_filter_on_last_modified_date_both_indexes(self):
        pub1 = IndexPublicationFactory.build(
            uuid="b38065ee-322e-46c7-ae64-c47112a4b408",
            laatst_gewijzigd_datum=datetime(2024, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
        )
        pub2 = IndexPublicationFactory.build(
            uuid="de225c2e-2700-4fee-a6ea-efa276db42d4",
            laatst_gewijzigd_datum=datetime(
                2022, 12, 10, 18, 0, 0, tzinfo=timezone.utc
            ),
        )
        doc1 = IndexDocumentFactory.build(
            uuid="6aac4fb2-d532-490b-bd6b-87b0257c0236",
            laatst_gewijzigd_datum=datetime(2024, 2, 11, 10, 0, 0, tzinfo=timezone.utc),
        )
        doc2 = IndexDocumentFactory.build(
            uuid="62fceb92-98bd-475c-b184-49ee8a274787",
            laatst_gewijzigd_datum=datetime(
                2022, 12, 10, 18, 0, 0, tzinfo=timezone.utc
            ),
        )
        index_publication(**pub1)
        index_publication(**pub2)
        index_document(**doc1)
        index_document(**doc2)

        response = self.client.post(
            self.url,
            {
                "laatst_gewijzigd_datum_vanaf": "2024-01-01T00:00:00+01:00",
                "laatst_gewijzigd_datum_tot": "2024-12-31T23:59:59.999999+01:00",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 2)
        expected_ids = {
            "b38065ee-322e-46c7-ae64-c47112a4b408",
            "6aac4fb2-d532-490b-bd6b-87b0257c0236",
        }
        ids = set(result["record"]["uuid"] for result in data["results"])
        self.assertEqual(ids, expected_ids)

    def test_filter_on_creatiedatum(self):
        doc1 = IndexDocumentFactory.build(
            uuid="6aac4fb2-d532-490b-bd6b-87b0257c0236",
            creatiedatum=date(2024, 2, 11),
        )
        doc2 = IndexDocumentFactory.build(
            uuid="62fceb92-98bd-475c-b184-49ee8a274787",
            creatiedatum=date(2022, 12, 10),
        )
        doc3 = IndexDocumentFactory.build(
            uuid="ef1dead2-e0f8-45be-acf7-3583adc14906",
            creatiedatum=date(2025, 1, 14),
        )
        index_document(**doc1)
        index_document(**doc2)
        index_document(**doc3)

        with self.subTest(creatiedatum_vanaf="2024-02-11", creatiedatum_tot=None):
            response = self.client.post(
                self.url, {"resultType": "document", "creatiedatumVanaf": "2024-02-11"}
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 2)
            expected_ids = {
                "6aac4fb2-d532-490b-bd6b-87b0257c0236",
                "ef1dead2-e0f8-45be-acf7-3583adc14906",
            }
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)

        with self.subTest(creatiedatum_vanaf=None, creatiedatum_tot="2022-12-10"):
            response = self.client.post(
                self.url, {"resultType": "document", "creatiedatumTot": "2022-12-10"}
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 1)
            expected_ids = {"62fceb92-98bd-475c-b184-49ee8a274787"}
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)

        with self.subTest(
            creatiedatum_vanaf="2024-01-01", creatiedatum_tot="2024-12-31"
        ):
            response = self.client.post(
                self.url,
                {
                    "resultType": "document",
                    "creatiedatumVanaf": "2024-01-01",
                    "creatiedatumTot": "2024-12-31",
                },
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 1)
            expected_ids = {"6aac4fb2-d532-490b-bd6b-87b0257c0236"}
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)
