from datetime import date, datetime, timezone

from django.urls import reverse_lazy

from rest_framework import status
from rest_framework.test import APITestCase

from woo_search.api.tests.mixin import APIKeyUnAuthorizedMixin, TokenAuthMixin
from woo_search.utils.tests.vcr import VCRMixin

from ..constants import SortChoices
from ..tasks import index_document, index_publication
from .base import ElasticSearchAPITestCase
from .factories import (
    IndexDocumentFactory,
    IndexPublicationFactory,
    InformationCategoryFactory,
    PublisherFactory,
)


class SearchApiAccessTest(APIKeyUnAuthorizedMixin, APITestCase):
    def test_api_with_wrong_credentials_blocks_access(self):
        url = reverse_lazy("api:search")

        self.assertWrongApiKeyProhibitsPostEndpointAccess(url)


class SearchApiTest(TokenAuthMixin, VCRMixin, ElasticSearchAPITestCase):
    url = reverse_lazy("api:search")
    maxDiff = None

    def test_no_body(self):
        index_publication(
            **IndexPublicationFactory.build(
                uuid="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
                laatst_gewijzigd_datum=datetime(
                    2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc
                ),
            )
        )
        index_document(
            **IndexDocumentFactory.build(
                uuid="525747fd-7e58-4005-8efa-59bcf4403385",
                laatst_gewijzigd_datum=datetime(
                    2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc
                ),
            )
        )

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 2)
        self.assertFalse(data["previous"])
        self.assertFalse(data["next"])
        results = data["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["type"], "publication")
        self.assertEqual(
            results[0]["record"]["uuid"], "6dae9be7-4f93-4aad-b56a-10b683b16dcc"
        )
        self.assertNotIn("publicatie", results[0]["record"])

        self.assertEqual(results[1]["type"], "document")
        self.assertEqual(
            results[1]["record"]["uuid"], "525747fd-7e58-4005-8efa-59bcf4403385"
        )
        self.assertIn("publicatie", results[1]["record"])

    def test_pagination_next_and_page_size(self):
        index_publication(
            **IndexPublicationFactory.build(
                uuid="1aa78d62-0cc7-4273-86b4-8c6bf4f28a98",
                laatst_gewijzigd_datum=datetime(
                    2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc
                ),
            )
        )
        index_document(
            **IndexDocumentFactory.build(
                uuid="85a095ea-e1fa-438c-9e05-1862874f57a0",
                laatst_gewijzigd_datum=datetime(
                    2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc
                ),
            )
        )

        response = self.client.post(self.url, {"page": 1, "pageSize": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 2)
        self.assertFalse(data["previous"])
        self.assertTrue(data["next"])
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["type"], "publication")

    def test_pagination_previous(self):
        index_publication(
            **IndexPublicationFactory.build(
                uuid="80485d67-0b97-4ed5-8483-f2d03d012e19",
                laatst_gewijzigd_datum=datetime(
                    2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc
                ),
            )
        )
        index_document(
            **IndexDocumentFactory.build(
                uuid="48981334-b480-4e7d-8c8d-925bbc67a969",
                laatst_gewijzigd_datum=datetime(
                    2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc
                ),
            )
        )

        response = self.client.post(self.url, {"page": 2, "pageSize": 1})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 2)
        self.assertTrue(data["previous"])
        self.assertFalse(data["next"])
        # test if results have the same length as the count
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["type"], "document")

    def test_sort_chronological(self):
        index_publication(
            **IndexPublicationFactory.build(
                uuid="0ce718e4-8fb5-42f1-a07e-cbf82a869efd",
                laatst_gewijzigd_datum=datetime(
                    2026, 1, 2, 12, 0, 0, tzinfo=timezone.utc
                ),
            )
        )
        index_document(
            **IndexDocumentFactory.build(
                uuid="3b3f4514-7d8b-4e31-83ca-fa9376ff6522",
                laatst_gewijzigd_datum=datetime(
                    2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc
                ),
            )
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
            **IndexPublicationFactory.build(
                uuid="5fc73bff-3cc2-4619-90d7-74b3eb3e4101",
            )
        )
        index_document(
            **IndexDocumentFactory.build(
                uuid="387d982b-d7c8-48e8-9665-2dbfb6f8688c",
            )
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
                [{"naam": "document", "count": 1}],
            )

    def test_boost_publication_over_document(self):
        # identifical hit conditions, boosting publication should result in the
        # publication being returned first.
        index_document(
            **IndexDocumentFactory.build(
                uuid="387d982b-d7c8-48e8-9665-2dbfb6f8688c",
                officiele_titel="Snowflake",
                # more recent, should become second element because of lower score since
                # publications are boosted
                laatst_gewijzigd_datum=datetime(
                    2025, 1, 10, 12, 0, 0, tzinfo=timezone.utc
                ),
            )
        )
        index_publication(
            **IndexPublicationFactory.build(
                uuid="5fc73bff-3cc2-4619-90d7-74b3eb3e4101",
                officiele_titel="Snowflake",
                laatst_gewijzigd_datum=datetime(
                    2025, 1, 5, 12, 0, 0, tzinfo=timezone.utc
                ),
            )
        )

        response = self.client.post(
            self.url, {"query": '"Snowflake"', "sort": SortChoices.relevance}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["count"], 2)
        first, second = data["results"]
        self.assertEqual(first["type"], "publication")
        self.assertEqual(second["type"], "document")

    def test_query(self):
        index_publication(
            **IndexPublicationFactory.build(
                uuid="50e32c44-515e-4c48-ae57-3aae82fc9cf1",
            )
        )
        index_document(
            **IndexDocumentFactory.build(
                uuid="6dd95a10-cc97-4f19-b7e4-2c85358acb98",
                identifier="document1",
            )
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
            **IndexDocumentFactory.build(
                uuid="3916925a-4260-4505-bfbb-0942113efd49",
                identifier="document1",
                officiele_titel="titel",
                verkorte_titel="snowflake",
                omschrijving="omschrijving",
            )
        )
        index_document(
            **IndexDocumentFactory.build(
                uuid="d49bc304-01a1-4eda-a914-a8dda5c901e2",
                identifier="snowflake",
                officiele_titel="titel",
                verkorte_titel="verkorte titel",
                omschrijving="omschrijving",
            )
        )
        index_document(
            **IndexDocumentFactory.build(
                uuid="bdcc4cea-b186-425e-8dcd-9fecb6818563",
                identifier="document3",
                officiele_titel="titel",
                verkorte_titel="verkorte titel",
                omschrijving="snowflake",
            )
        )
        index_document(
            **IndexDocumentFactory.build(
                uuid="7eade718-bccb-4876-9f00-a095beebc360",
                identifier="document4",
                officiele_titel="snowflake",
                verkorte_titel="verkorte titel",
                omschrijving="omschrijving",
            )
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

        with self.subTest(
            creatiedatum_vanaf="2024-02-11", creatiedatum_tot_en_met=None
        ):
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

        with self.subTest(
            creatiedatum_vanaf=None, creatiedatum_tot_en_met="2022-12-10"
        ):
            response = self.client.post(
                self.url,
                {"resultType": "document", "creatiedatumTotEnMet": "2022-12-10"},
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 1)
            expected_ids = {"62fceb92-98bd-475c-b184-49ee8a274787"}
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)

        with self.subTest(
            creatiedatum_vanaf="2024-01-01", creatiedatum_tot_en_met="2024-12-31"
        ):
            response = self.client.post(
                self.url,
                {
                    "resultType": "document",
                    "creatiedatumVanaf": "2024-01-01",
                    "creatiedatumTotEnMet": "2024-12-31",
                },
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 1)
            expected_ids = {"6aac4fb2-d532-490b-bd6b-87b0257c0236"}
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)

    def test_filter_by_publisher_uuid(self):
        publisher_1 = PublisherFactory.build(
            uuid="f9cc8c26-7ce7-4a25-9554-e6a2892176d7",
            naam="Dimpact",
        )
        publisher_2 = PublisherFactory.build(
            uuid="e0eb40f7-eacb-45dc-973a-2e8480f49b76",
            naam="Maycatt",
        )
        doc1 = IndexDocumentFactory.build(
            uuid="8bca9140-81f6-46f0-823a-31184e10ff66",
            publisher=publisher_1,
        )
        # document with random publisher, must not be a hit
        doc2 = IndexDocumentFactory.build(uuid="0ea8b96e-cca5-45df-9797-abf9cfef3ed6")
        pub1 = IndexPublicationFactory.build(
            uuid="dd3b8be0-e461-498a-9a18-0f5fc8adc956",
            publisher=publisher_2,
        )
        # publication with random publisher, must not be a hit
        pub2 = IndexPublicationFactory.build(
            uuid="3d6f91fc-ce3b-45d0-b3d6-c304be03845d"
        )
        index_publication(**pub1)
        index_publication(**pub2)
        index_document(**doc1)
        index_document(**doc2)

        with self.subTest("query with non-existing UUID"):
            response = self.client.post(
                self.url,
                {"publishers": ["1934d1db-b5c8-4521-97fe-a2ef969dd84e"]},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["count"], 0)

        with self.subTest("expect match on one of provided UUIDs"):
            response = self.client.post(
                self.url,
                {
                    "publishers": [
                        "f9cc8c26-7ce7-4a25-9554-e6a2892176d7",
                        "e0eb40f7-eacb-45dc-973a-2e8480f49b76",
                    ]
                },
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 2)
            expected_ids = {
                "8bca9140-81f6-46f0-823a-31184e10ff66",
                "dd3b8be0-e461-498a-9a18-0f5fc8adc956",
            }
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)
            # assert on the buckets
            self.assertIn("facets", data)
            self.assertIn("publishers", data["facets"])
            facets_by_id = {
                publisher["uuid"]: publisher
                for publisher in data["facets"]["publishers"]
            }
            self.assertEqual(len(facets_by_id), 2)
            self.assertEqual(
                facets_by_id["f9cc8c26-7ce7-4a25-9554-e6a2892176d7"],
                {
                    "uuid": "f9cc8c26-7ce7-4a25-9554-e6a2892176d7",
                    "naam": "Dimpact",
                    "count": 1,
                },
            )
            self.assertEqual(
                facets_by_id["e0eb40f7-eacb-45dc-973a-2e8480f49b76"],
                {
                    "uuid": "e0eb40f7-eacb-45dc-973a-2e8480f49b76",
                    "naam": "Maycatt",
                    "count": 1,
                },
            )

    def test_filter_by_information_category_uuid(self):
        ic_1 = InformationCategoryFactory.build(
            uuid="f9cc8c26-7ce7-4a25-9554-e6a2892176d7",
            naam="Inspanningsverplichting",
        )
        ic_2 = InformationCategoryFactory.build(
            uuid="e0eb40f7-eacb-45dc-973a-2e8480f49b76",
            naam="WOO",
        )
        doc1 = IndexDocumentFactory.build(
            uuid="8bca9140-81f6-46f0-823a-31184e10ff66",
            informatie_categorieen=[ic_1],
        )
        # document with random information categories, must not be a hit
        doc2 = IndexDocumentFactory.build(uuid="0ea8b96e-cca5-45df-9797-abf9cfef3ed6")
        pub1 = IndexPublicationFactory.build(
            uuid="dd3b8be0-e461-498a-9a18-0f5fc8adc956",
            informatie_categorieen=[ic_2],
        )
        # publication with random information categories, must not be a hit
        pub2 = IndexPublicationFactory.build(
            uuid="3d6f91fc-ce3b-45d0-b3d6-c304be03845d"
        )
        index_publication(**pub1)
        index_publication(**pub2)
        index_document(**doc1)
        index_document(**doc2)

        with self.subTest("query with non-existing UUID"):
            response = self.client.post(
                self.url,
                {"informatieCategorieen": ["1934d1db-b5c8-4521-97fe-a2ef969dd84e"]},
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["count"], 0)

        with self.subTest("expect match on one of provided UUIDs"):
            response = self.client.post(
                self.url,
                {
                    "informatieCategorieen": [
                        "f9cc8c26-7ce7-4a25-9554-e6a2892176d7",
                        "e0eb40f7-eacb-45dc-973a-2e8480f49b76",
                    ]
                },
            )

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["count"], 2)
            expected_ids = {
                "8bca9140-81f6-46f0-823a-31184e10ff66",
                "dd3b8be0-e461-498a-9a18-0f5fc8adc956",
            }
            ids = set(result["record"]["uuid"] for result in data["results"])
            self.assertEqual(ids, expected_ids)
            # assert on the buckets
            self.assertIn("facets", data)
            self.assertIn("informatieCategorieen", data["facets"])
            facets_by_id = {
                publisher["uuid"]: publisher
                for publisher in data["facets"]["informatieCategorieen"]
            }
            self.assertEqual(len(facets_by_id), 2)
            self.assertEqual(
                facets_by_id["f9cc8c26-7ce7-4a25-9554-e6a2892176d7"],
                {
                    "uuid": "f9cc8c26-7ce7-4a25-9554-e6a2892176d7",
                    "naam": "Inspanningsverplichting",
                    "count": 1,
                },
            )
            self.assertEqual(
                facets_by_id["e0eb40f7-eacb-45dc-973a-2e8480f49b76"],
                {
                    "uuid": "e0eb40f7-eacb-45dc-973a-2e8480f49b76",
                    "naam": "WOO",
                    "count": 1,
                },
            )
