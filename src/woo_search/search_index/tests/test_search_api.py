from datetime import date, datetime, timezone

from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.test import APITestCase

from woo_search.api.tests.mixin import APIKeyUnAuthorizedMixin, TokenAuthMixin
from woo_search.utils.tests.vcr import VCRMixin

from ..constants import ResultTypeChoices
from ..tasks import index_document, index_publication
from .base import ElasticSearchAPITestCase


class SearchApiAccessTest(APIKeyUnAuthorizedMixin, APITestCase):
    def test_api_with_wrong_credentials_blocks_access(self):
        url = reverse_lazy("api:search")

        self.assertWrongApiKeyProhibitsPostEndpointAccess(url)


class SearchApiTest(TokenAuthMixin, VCRMixin, ElasticSearchAPITestCase):
    url = reverse_lazy("api:search")

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
            identifier="https://www.example.com/1",
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
                    "identifier": "https://www.example.com/1",
                    "officieleTitel": "A test document",
                    "verkorteTitel": "A document",
                    "omschrijving": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "creatiedatum": "2026-01-01T00:00:00+01:00",
                    "registratiedatum": "2026-01-05T12:00:00+00:00",
                    "laatstGewijzigdDatum": "2026-01-05T12:00:00+00:00",
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
                    "registratiedatum": "2026-01-05T12:00:00+00:00",
                    "laatstGewijzigdDatum": "2026-01-05T12:00:00+00:00",
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
            identifier="https://www.example.com/1",
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

        self.assertEqual(data["count"], 1)
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
            identifier="https://www.example.com/1",
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

        self.assertEqual(data["count"], 1)
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
            identifier="https://www.example.com/1",
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
            identifier="https://www.example.com/1",
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
        self.assertFalse(data["previous"])
        self.assertFalse(data["next"])
        # test if results have the same length as the count
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["type"], "document")

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
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        response = self.client.post(self.url, {"query": "https://www.example.com/1"})

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
            identifier="https://www.testsite.com/999",
            officiele_titel="titel",
            verkorte_titel="https://www.example.com/1",
            omschrijving="omschijving",
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
            identifier="https://www.example.com/1",
            officiele_titel="titel",
            verkorte_titel="verkorte titel",
            omschrijving="omschijving",
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
            identifier="https://www.testsite.com/999",
            officiele_titel="titel",
            verkorte_titel="verkorte titel",
            omschrijving="https://www.example.com/1",
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
            identifier="https://www.testsite.com/999",
            officiele_titel="https://www.example.com/1",
            verkorte_titel="verkorte titel",
            omschrijving="omschijving",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        response = self.client.post(self.url, {"query": "https://www.example.com/1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 4)
        self.assertFalse(data["previous"])
        self.assertFalse(data["next"])
        # see if the field priority goes as following:
        # - identifier
        # - officiele_titel
        # - verkorte_titel
        # - omschijving
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

    def test_search_creatiedatum_filters(self):
        index_document(
            uuid="f86a03ce-7b36-4f40-a64d-89670ebab9df",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="d8313c1a-7a0d-45d1-88a8-356a20772ecb",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 3),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        with self.subTest("creatiedatum vanaf"):
            response = self.client.post(self.url, {"creatiedatumVanaf": "2026-01-02"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 1)
            self.assertEqual(
                data["results"][0]["record"]["uuid"],
                "d8313c1a-7a0d-45d1-88a8-356a20772ecb",
            )
            self.assertEqual(data["results"][0]["record"]["creatiedatum"], "2026-01-03")

        with self.subTest("creatiedatum tot"):
            response = self.client.post(self.url, {"creatiedatumTot": "2026-01-02"})

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 1)
            self.assertEqual(
                data["results"][0]["record"]["uuid"],
                "f86a03ce-7b36-4f40-a64d-89670ebab9df",
            )
            self.assertEqual(data["results"][0]["record"]["creatiedatum"], "2026-01-01")

        with self.subTest("creatiedatum vanaf and tot"):
            response = self.client.post(
                self.url,
                {"creatiedatumVanaf": "2026-01-01", "creatiedatumTot": "2026-01-02"},
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 1)
            self.assertEqual(
                data["results"][0]["record"]["uuid"],
                "f86a03ce-7b36-4f40-a64d-89670ebab9df",
            )
            self.assertEqual(data["results"][0]["record"]["creatiedatum"], "2026-01-01")

        for filter_name in ["creatiedatumVanaf", "creatiedatumTot"]:
            with self.subTest(
                f"if resultType is publication combined with {filter_name} raise error"
            ):
                response = self.client.post(
                    self.url,
                    {
                        filter_name: "2026-01-01",
                        "resultType": ResultTypeChoices.publication,
                    },
                )

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertEqual(
                    response.json(),
                    {
                        "resultType": [
                            _(
                                "Cannot filter on {publication} when filtering on a field only present in {document}.".format(
                                    publication=ResultTypeChoices.publication,
                                    document=ResultTypeChoices.document,
                                )
                            )
                        ]
                    },
                )

            with self.subTest(
                "if resultType is document combined with {filter_name} do not raise error"
            ):
                response = self.client.post(
                    self.url,
                    {
                        filter_name: "2026-01-01",
                        "resultType": ResultTypeChoices.document,
                    },
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_registratiedatum_filters(self):
        index_document(
            uuid="c0cda71d-28b5-46b8-aef2-8682ada73f33",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 6, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="914f9d85-fa70-4257-a691-5b9dd78eb3c6",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        with self.subTest("registratiedatum vanaf"):
            response = self.client.post(
                self.url, {"registratiedatumVanaf": "2026-01-05T09:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 1)
            self.assertEqual(
                data["results"][0]["record"]["uuid"],
                "914f9d85-fa70-4257-a691-5b9dd78eb3c6",
            )
            self.assertEqual(
                data["results"][0]["record"]["registratiedatum"],
                "2026-01-05T12:00:00+00:00",
            )

        with self.subTest("creatiedatum tot"):
            response = self.client.post(
                self.url, {"registratiedatumTot": "2026-01-05T09:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 1)
            self.assertEqual(
                data["results"][0]["record"]["uuid"],
                "c0cda71d-28b5-46b8-aef2-8682ada73f33",
            )
            self.assertEqual(
                data["results"][0]["record"]["registratiedatum"],
                "2026-01-05T06:00:00+00:00",
            )

        with self.subTest("creatiedatum vanaf and tot"):
            response = self.client.post(
                self.url,
                {
                    "registratiedatumVanaf": "2026-01-05T06:00:00+00:00",
                    "registratiedatumTot": "2026-01-05T09:00:00+00:00",
                },
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 1)
            self.assertEqual(
                data["results"][0]["record"]["uuid"],
                "c0cda71d-28b5-46b8-aef2-8682ada73f33",
            )
            self.assertEqual(
                data["results"][0]["record"]["registratiedatum"],
                "2026-01-05T06:00:00+00:00",
            )

    def test_search_laatst_gewijzigd_datum_filters(self):
        index_document(
            uuid="a1b1739f-2eea-4d2b-891b-cb6b52523cca",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 6, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="3ed11598-0dfe-4784-83ed-c9ecec77d2f6",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        with self.subTest("laatst gewijzigd datum vanaf"):
            response = self.client.post(
                self.url, {"laatstGewijzigdDatumVanaf": "2026-01-05T09:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 1)
            self.assertEqual(
                data["results"][0]["record"]["uuid"],
                "3ed11598-0dfe-4784-83ed-c9ecec77d2f6",
            )
            self.assertEqual(
                data["results"][0]["record"]["laatstGewijzigdDatum"],
                "2026-01-05T12:00:00+00:00",
            )

        with self.subTest("laatst gewijzigd datum tot"):
            response = self.client.post(
                self.url, {"laatstGewijzigdDatumTot": "2026-01-05T09:00:00+00:00"}
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 1)
            self.assertEqual(
                data["results"][0]["record"]["uuid"],
                "a1b1739f-2eea-4d2b-891b-cb6b52523cca",
            )
            self.assertEqual(
                data["results"][0]["record"]["laatstGewijzigdDatum"],
                "2026-01-05T06:00:00+00:00",
            )

        with self.subTest("laatst gewijzigd datum vanaf and tot"):
            response = self.client.post(
                self.url,
                {
                    "laatstGewijzigdDatumVanaf": "2026-01-05T06:00:00+00:00",
                    "laatstGewijzigdDatumTot": "2026-01-05T09:00:00+00:00",
                },
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 1)
            self.assertEqual(
                data["results"][0]["record"]["uuid"],
                "a1b1739f-2eea-4d2b-891b-cb6b52523cca",
            )
            self.assertEqual(
                data["results"][0]["record"]["laatstGewijzigdDatum"],
                "2026-01-05T06:00:00+00:00",
            )

    def test_search_combine_multiple_datum_filters(self):
        index_document(
            uuid="a1b1739f-2eea-4d2b-891b-cb6b52523cca",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 6, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="3ed11598-0dfe-4784-83ed-c9ecec77d2f6",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "2f809be7-b585-4cb8-8010-9682c4281aec",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        response = self.client.post(
            self.url,
            {
                "creatiedatumVanaf": "2026-01-01",
                "laatstGewijzigdDatumTot": "2026-01-05T09:00:00+00:00",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(data["count"], 1)
        self.assertEqual(
            data["results"][0]["record"]["uuid"],
            "a1b1739f-2eea-4d2b-891b-cb6b52523cca",
        )
        self.assertEqual(
            data["results"][0]["record"]["creatiedatum"],
            "2026-01-01",
        )
        self.assertEqual(
            data["results"][0]["record"]["laatstGewijzigdDatum"],
            "2026-01-05T06:00:00+00:00",
        )

    def test_search_publishers(self):
        index_document(
            uuid="5e0d7a0b-aab9-4721-b6a7-9ff55894441f",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "62da7e9d-2481-4d46-9c77-563b490126aa",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 6, 0, 0, tzinfo=timezone.utc),
        )
        index_document(
            uuid="330a4e59-f9f6-4742-98dd-e7be8190b423",
            publicatie="6dae9be7-4f93-4aad-b56a-10b683b16dcc",
            publisher={
                "uuid": "ff1d57e8-5f45-427a-b6d9-7f6d80c0e1dc",
                "naam": "Amsterdam",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        index_publication(
            uuid="573552d3-1f30-425d-9949-b4003a74d7f5",
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
        index_publication(
            uuid="8cbb096a-173e-472f-94b7-9e9936675b66",
            publisher={
                "uuid": "52b7bb6e-5735-42e7-9843-7fce610c46a3",
                "naam": "Groningen",
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

        with self.subTest("test with single uuid"):
            # uuid of utrecht
            response = self.client.post(
                self.url,
                {"publishers": ["62da7e9d-2481-4d46-9c77-563b490126aa"]},
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 2)
            self.assertEqual(
                data["results"][0]["record"]["publisher"]["uuid"],
                "62da7e9d-2481-4d46-9c77-563b490126aa",
            )
            self.assertEqual(
                data["results"][1]["record"]["publisher"]["uuid"],
                "62da7e9d-2481-4d46-9c77-563b490126aa",
            )

        with self.subTest("test with multiple uuids"):
            # uuid of Groningen and Amsterdam
            response = self.client.post(
                self.url,
                {
                    "publishers": [
                        "52b7bb6e-5735-42e7-9843-7fce610c46a3",
                        "ff1d57e8-5f45-427a-b6d9-7f6d80c0e1dc",
                    ]
                },
            )

            self.assertEqual(response.status_code, status.HTTP_200_OK)

            data = response.json()

            self.assertEqual(data["count"], 2)
            self.assertEqual(
                data["results"][0]["record"]["publisher"]["uuid"],
                "ff1d57e8-5f45-427a-b6d9-7f6d80c0e1dc",
            )
            self.assertEqual(
                data["results"][1]["record"]["publisher"]["uuid"],
                "52b7bb6e-5735-42e7-9843-7fce610c46a3",
            )
