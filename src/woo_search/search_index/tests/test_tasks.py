from datetime import UTC, date, datetime

from django.test import override_settings

from elasticsearch import NotFoundError

from woo_search.utils.tests.vcr import VCRMixin

from ..client import get_client
from ..index import Document, Publication, Topic
from ..tasks import (
    index_document,
    index_publication,
    index_topic,
    remove_document_from_index,
    remove_publication_from_index,
    remove_topic_from_index,
)
from .base import ElasticSearchTestCase
from .factories import (
    IndexDocumentFactory,
    IndexPublicationFactory,
    IndexTopicFactory,
    ServiceFactory,
)


class DocumentTaskTest(VCRMixin, ElasticSearchTestCase):
    def test_index_document_roundtrip(self):
        document_uuid = "0095704d-4216-4de3-83d2-20dba551b0dc"

        index_document(
            uuid=document_uuid,
            publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
            informatie_categorieen=[
                {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
            ],
            onderwerpen=[
                {
                    "uuid": "31e893cc-1669-4d01-9118-fc404d21c0d7",
                    "officiele_titel": "Inspanning",
                },
            ],
            publisher={
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
        )

        # verify that it's indexed
        with get_client() as client:
            doc = Document.get(
                using=client,
                id=document_uuid,
            )

        # helps with type narrowing :)
        assert isinstance(doc, Document), "Expected doc to be indexed"
        # Assert the provided data is indexed properly.
        self.assertEqual(doc.uuid, "0095704d-4216-4de3-83d2-20dba551b0dc")
        self.assertEqual(doc.publicatie, "d481bea6-335b-4d90-9b27-ac49f7196633")
        self.assertEqual(
            doc.informatie_categorieen,
            [{"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}],
        )
        self.assertEqual(
            doc.onderwerpen,
            [
                {
                    "uuid": "31e893cc-1669-4d01-9118-fc404d21c0d7",
                    "officiele_titel": "Inspanning",
                },
            ],
        )
        self.assertEqual(
            doc.publisher,
            {
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
        )
        self.assertEqual(doc.identifier, "https://www.example.com/1")
        self.assertEqual(doc.officiele_titel, "A test document")
        self.assertEqual(doc.verkorte_titel, "A document")
        self.assertEqual(
            doc.omschrijving, "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        )
        # date -> converted to naive datetime
        self.assertEqual(doc.creatiedatum, date(2026, 1, 1))
        self.assertEqual(
            doc.registratiedatum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
        )
        self.assertEqual(
            doc.laatst_gewijzigd_datum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
        )

        with self.subTest("re-indexing data with same UUID updates values"):
            index_document(
                uuid=document_uuid,
                publicatie="CHANGED",
                informatie_categorieen=[
                    {
                        "uuid": "c9001845-aef0-4150-bbf0-a5f5c096e603",
                        "naam": "Inspanningsverplichting",
                    }
                ],
                onderwerpen=[
                    {
                        "uuid": "d80502e9-467a-44c2-94fa-e26d5bb1fa12",
                        "officiele_titel": "GPP",
                    },
                ],
                publisher={
                    "uuid": "CHANGED",
                    "naam": "Amsterdam",
                },
                identifier="https://www.example.com/999",
                officiele_titel="CHANGED TITLE",
                verkorte_titel="CHANGED",
                omschrijving="CHANGED OMSCHRIJVING",
                creatiedatum=date(2030, 1, 1),
                registratiedatum=datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
                laatst_gewijzigd_datum=datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
            )

            with get_client() as client:
                updated_doc = Document.get(
                    using=client,
                    id=document_uuid,
                )

            assert isinstance(updated_doc, Document), "Expected doc to be indexed"
            # Assert the provided data is indexed properly.
            self.assertEqual(updated_doc.uuid, "0095704d-4216-4de3-83d2-20dba551b0dc")
            self.assertEqual(updated_doc.publicatie, "CHANGED")
            self.assertEqual(
                updated_doc.informatie_categorieen,
                [
                    {
                        "uuid": "c9001845-aef0-4150-bbf0-a5f5c096e603",
                        "naam": "Inspanningsverplichting",
                    }
                ],
            )
            self.assertEqual(
                updated_doc.onderwerpen,
                [
                    {
                        "uuid": "d80502e9-467a-44c2-94fa-e26d5bb1fa12",
                        "officiele_titel": "GPP",
                    },
                ],
            )
            self.assertEqual(
                doc.onderwerpen,
                [
                    {
                        "uuid": "31e893cc-1669-4d01-9118-fc404d21c0d7",
                        "officiele_titel": "Inspanning",
                    },
                ],
            )
            self.assertEqual(
                updated_doc.publisher,
                {
                    "uuid": "CHANGED",
                    "naam": "Amsterdam",
                },
            )
            self.assertEqual(updated_doc.identifier, "https://www.example.com/999")
            self.assertEqual(updated_doc.officiele_titel, "CHANGED TITLE")
            self.assertEqual(updated_doc.verkorte_titel, "CHANGED")
            self.assertEqual(updated_doc.omschrijving, "CHANGED OMSCHRIJVING")
            # date -> converted to naive datetime
            self.assertEqual(updated_doc.creatiedatum, date(2030, 1, 1))
            self.assertEqual(
                updated_doc.registratiedatum,
                datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
            )
            self.assertEqual(
                updated_doc.laatst_gewijzigd_datum,
                datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
            )

    def test_full_text_upload(self):
        ServiceFactory.create(for_download_url_mock_service=True)
        with self.subTest("Happy flow"):
            document_uuid = "e90b8ea2-1ac2-4ef9-80ed-059d69eb3c54"

            index_document(
                uuid=document_uuid,
                publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
                informatie_categorieen=[
                    {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
                ],
                onderwerpen=[
                    {
                        "uuid": "63074d74-ba3d-4d28-864e-cdf825646342",
                        "officiele_titel": "GPP",
                    }
                ],
                publisher={
                    "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                    "naam": "Utrecht",
                },
                identifier="https://www.example.com/1",
                officiele_titel="A test document",
                verkorte_titel="A document",
                omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                creatiedatum=date(2026, 1, 1),
                registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                download_url="http://localhost/document/c80fcb40-f6af-44a4-90ab-07f75b47e9cb",
                file_size=1000,
            )

            # verify that it's indexed
            with get_client() as client:
                doc_source = client.get(index="document", id=document_uuid)["_source"]

            self.assertEqual(
                doc_source["document_data"][0]["attachment"]["content"],
                "Document 'c80fcb40-f6af-44a4-90ab-07f75b47e9cb'",
            )

        with self.subTest(
            "Download url with no content doesn't create attachment field in index."
        ):
            document_uuid = "9acc8148-b498-4c15-b2df-0f26d41ff4c2"

            index_document(
                uuid=document_uuid,
                publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
                informatie_categorieen=[
                    {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
                ],
                onderwerpen=[
                    {
                        "uuid": "63074d74-ba3d-4d28-864e-cdf825646342",
                        "officiele_titel": "GPP",
                    }
                ],
                publisher={
                    "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                    "naam": "Utrecht",
                },
                identifier="https://www.example.com/1",
                officiele_titel="A test document",
                verkorte_titel="A document",
                omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                creatiedatum=date(2026, 1, 1),
                registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                download_url="http://localhost/document/empty",
                file_size=1000,
            )

            # verify that it's indexed
            with get_client() as client:
                doc_source = client.get(index="document", id=document_uuid)["_source"]

            self.assertEqual(doc_source["document_data"][0]["attachment"], {})

        with self.subTest(
            "Download url raises error creates empty attachment field in index."
        ):
            document_uuid = "9acc8148-b498-4c15-b2df-0f26d41ff4c2"

            index_document(
                uuid=document_uuid,
                publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
                informatie_categorieen=[
                    {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
                ],
                onderwerpen=[
                    {
                        "uuid": "63074d74-ba3d-4d28-864e-cdf825646342",
                        "officiele_titel": "GPP",
                    }
                ],
                publisher={
                    "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                    "naam": "Utrecht",
                },
                identifier="https://www.example.com/1",
                officiele_titel="A test document",
                verkorte_titel="A document",
                omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                creatiedatum=date(2026, 1, 1),
                registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                download_url="http://localhost/document/error",
                file_size=1000,
            )

            # verify that it's indexed
            with get_client() as client:
                doc_source = client.get(index="document", id=document_uuid)["_source"]

            self.assertNotIn("document_data", doc_source)

    def test_full_text_upload_download_url_service_unauthorized(self):
        ServiceFactory.create(
            for_download_url_mock_service=True, header_value="Token wrong-token"
        )

        document_uuid = "9acc8148-b498-4c15-b2df-0f26d41ff4c2"

        index_document(
            uuid=document_uuid,
            publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
            informatie_categorieen=[
                {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
            ],
            onderwerpen=[
                {
                    "uuid": "63074d74-ba3d-4d28-864e-cdf825646342",
                    "officiele_titel": "GPP",
                }
            ],
            publisher={
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            download_url="https://www.example.com/downloads/1",
            file_size=1000,
        )

        # verify that it's indexed
        with get_client() as client:
            doc_source = client.get(index="document", id=document_uuid)["_source"]

        self.assertNotIn("document_data", doc_source)

    @override_settings(
        SEARCH_INDEX={
            "HOST": "http://localhost:9201",
            "USER": "",
            "PASSWORD": "",
            "TIMEOUT": 3,
            "CA_CERTS": "",
            "REFRESH": "wait_for",
            "INDEXED_CHARS": -1,
            "MAX_INDEX_FILE_SIZE": 1000,  # byte
        }
    )
    def test_full_text_upload_with_max_file_size(self):
        ServiceFactory.create(for_download_url_mock_service=True)

        with self.subTest(
            "Don't index full document text when no file_size was given."
        ):
            document_uuid = "ed19d46e-c367-4410-a891-88f20d232a03"

            index_document(
                uuid=document_uuid,
                publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
                informatie_categorieen=[
                    {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
                ],
                onderwerpen=[
                    {
                        "uuid": "63074d74-ba3d-4d28-864e-cdf825646342",
                        "officiele_titel": "GPP",
                    }
                ],
                publisher={
                    "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                    "naam": "Utrecht",
                },
                identifier="https://www.example.com/1",
                officiele_titel="A test document",
                verkorte_titel="A document",
                omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                creatiedatum=date(2026, 1, 1),
                registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                download_url="http://localhost/document/8decfefc-9879-45e8-8641-2096bbd5dba8",
            )

            # verify that it's indexed
            with get_client() as client:
                doc_source = client.get(index="document", id=document_uuid)["_source"]

            self.assertNotIn("document_data", doc_source)

        with self.subTest(
            "if given file_size is higher then max_file_size don't index full "
            "document text."
        ):
            document_uuid = "da97b6cb-7211-4762-9673-21a08f508e85 "

            index_document(
                uuid=document_uuid,
                publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
                informatie_categorieen=[
                    {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
                ],
                onderwerpen=[
                    {
                        "uuid": "63074d74-ba3d-4d28-864e-cdf825646342",
                        "officiele_titel": "GPP",
                    }
                ],
                publisher={
                    "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                    "naam": "Utrecht",
                },
                identifier="https://www.example.com/1",
                officiele_titel="A test document",
                verkorte_titel="A document",
                omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                creatiedatum=date(2026, 1, 1),
                registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                download_url="http://localhost/document/8decfefc-9879-45e8-8641-2096bbd5dba8",
                file_size=2000,
            )

            # verify that it's indexed
            with get_client() as client:
                doc_source = client.get(index="document", id=document_uuid)["_source"]

            self.assertNotIn("attachment", doc_source)

        with self.subTest(
            "index full document text if file size is lower then the max configured "
            "size."
        ):
            document_uuid = "554be64c-e6af-49b5-8af5-80e83155212d"

            index_document(
                uuid=document_uuid,
                publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
                informatie_categorieen=[
                    {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
                ],
                onderwerpen=[
                    {
                        "uuid": "63074d74-ba3d-4d28-864e-cdf825646342",
                        "officiele_titel": "GPP",
                    }
                ],
                publisher={
                    "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                    "naam": "Utrecht",
                },
                identifier="https://www.example.com/1",
                officiele_titel="A test document",
                verkorte_titel="A document",
                omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                creatiedatum=date(2026, 1, 1),
                registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
                download_url="http://localhost/document/8decfefc-9879-45e8-8641-2096bbd5dba8",
                file_size=800,
            )

            # verify that it's indexed
            with get_client() as client:
                doc_source = client.get(index="document", id=document_uuid)["_source"]

            self.assertEqual(
                doc_source["document_data"][0]["attachment"]["content"],
                "Document '8decfefc-9879-45e8-8641-2096bbd5dba8'",
            )

    def test_update_full_document_text(self):
        ServiceFactory.create(for_download_url_mock_service=True)
        document_uuid = "e62db63f-9e99-41a4-88a9-be9cc3d7509a"

        index_document(
            uuid=document_uuid,
            publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
            informatie_categorieen=[
                {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
            ],
            onderwerpen=[
                {
                    "uuid": "31e893cc-1669-4d01-9118-fc404d21c0d7",
                    "officiele_titel": "Inspanning",
                },
            ],
            publisher={
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            download_url="http://localhost/document/ff2c18cf-8165-45d3-873d-b68e676f99ff",
            file_size=1000,
        )

        # verify that it's indexed
        with get_client() as client:
            doc_source = client.get(index="document", id=document_uuid)["_source"]

        self.assertEqual(
            doc_source["document_data"][0]["attachment"]["content"],
            "Document 'ff2c18cf-8165-45d3-873d-b68e676f99ff'",
        )

        # Update document data by changing response content from url
        index_document(
            uuid=document_uuid,
            publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
            informatie_categorieen=[
                {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
            ],
            onderwerpen=[
                {
                    "uuid": "1fca87c8-cadf-4643-b9e6-10f0071ed80d",
                    "officiele_titel": "GPP",
                },
            ],
            publisher={
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            download_url="http://localhost/document/8decfefc-9879-45e8-8641-2096bbd5dba8",
            file_size=1000,
        )

        # verify that it's indexed
        with get_client() as client:
            doc_source = client.get(index="document", id=document_uuid)["_source"]

        self.assertEqual(
            doc_source["document_data"][0]["attachment"]["content"],
            "Document '8decfefc-9879-45e8-8641-2096bbd5dba8'",
        )

    def test_download_zip_document(self):
        ServiceFactory.create(for_download_url_mock_service=True)
        document_uuid = "f5a98468-92ef-49a1-8dff-4a7c682347f8"

        index_document(
            uuid=document_uuid,
            publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
            informatie_categorieen=[
                {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
            ],
            onderwerpen=[
                {
                    "uuid": "31e893cc-1669-4d01-9118-fc404d21c0d7",
                    "officiele_titel": "Inspanning",
                },
            ],
            publisher={
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            download_url="http://localhost/document/zip",
            file_size=1000,
        )

        # verify that it's indexed
        with get_client() as client:
            doc_source = client.get(index="document", id=document_uuid)["_source"]

        self.assertEqual(len(doc_source["document_data"]), 2)
        self.assertEqual(
            doc_source["document_data"][0]["attachment"]["content"],
            "test1",
        )
        self.assertEqual(
            doc_source["document_data"][1]["attachment"]["content"],
            "test2",
        )

    @override_settings(
        SEARCH_INDEX={
            "HOST": "http://localhost:9201",
            "USER": "",
            "PASSWORD": "",
            "TIMEOUT": 3,
            "CA_CERTS": "",
            "REFRESH": "wait_for",
            "INDEXED_CHARS": -1,
            "MAX_INDEX_FILE_SIZE": 1000,  # byte
        }
    )
    def test_download_7zip_document(self):
        ServiceFactory.create(for_download_url_mock_service=True)
        document_uuid = "d9fe4844-bdf8-4d66-b613-4efa71598105"

        index_document(
            uuid=document_uuid,
            publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
            informatie_categorieen=[
                {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
            ],
            onderwerpen=[
                {
                    "uuid": "31e893cc-1669-4d01-9118-fc404d21c0d7",
                    "officiele_titel": "Inspanning",
                },
            ],
            publisher={
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            download_url="http://localhost/document/7zip",
            file_size=401,
        )

        # verify that it's indexed
        with get_client() as client:
            doc_source = client.get(index="document", id=document_uuid)["_source"]

        # test that only files up to 1000 bytes get indexed.
        # This excludes the test3 file which is 1mb.
        self.assertEqual(len(doc_source["document_data"]), 2)
        self.assertEqual(
            doc_source["document_data"][0]["attachment"]["content"],
            "test1",
        )
        self.assertEqual(
            doc_source["document_data"][1]["attachment"]["content"],
            "test2",
        )

    def test_full_document_text_index_without_service_configured(self):
        document_uuid = "e62db63f-9e99-41a4-88a9-be9cc3d7509a"

        index_document(
            uuid=document_uuid,
            publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
            informatie_categorieen=[
                {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
            ],
            onderwerpen=[
                {
                    "uuid": "31e893cc-1669-4d01-9118-fc404d21c0d7",
                    "officiele_titel": "GPP",
                },
            ],
            publisher={
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
                "naam": "Utrecht",
            },
            identifier="https://www.example.com/1",
            officiele_titel="A test document",
            verkorte_titel="A document",
            omschrijving="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            creatiedatum=date(2026, 1, 1),
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            download_url="https://www.example.com/downloads/1",
            file_size=1000,
        )

        # verify that it's indexed
        with get_client() as client:
            doc_source = client.get(index="document", id=document_uuid)["_source"]

        self.assertNotIn("document_data", doc_source)


class PublicationTaskTest(VCRMixin, ElasticSearchTestCase):
    def test_index_publication_roundtrip(self):
        publication_uuid = "55b66c11-7cc9-4c50-bffa-7956e0edacef"

        index_publication(
            uuid=publication_uuid,
            publisher={
                "uuid": "07061b66-3cdc-494c-959a-22a59a92a0c4",
                "naam": "Utrecht",
            },
            informatie_categorieen=[
                {"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}
            ],
            onderwerpen=[
                {
                    "uuid": "6deb195e-28d0-4d35-b267-418c9f30b772",
                    "officiele_titel": "GPP",
                }
            ],
            officiele_titel="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            verkorte_titel="Donec finibus non tortor quis sollicitudin.",
            omschrijving="Nulla at nisi at enim eleifend facilisis at vitae velit.",
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
        )

        # verify that it's indexed
        with get_client() as client:
            publication = Publication.get(
                using=client,
                id=publication_uuid,
            )

        # helps with type narrowing :)
        assert isinstance(publication, Publication), "Expected doc to be indexed"
        # Assert the provided data is indexed properly.
        self.assertEqual(publication.uuid, "55b66c11-7cc9-4c50-bffa-7956e0edacef")
        self.assertEqual(
            publication.publisher,
            {"uuid": "07061b66-3cdc-494c-959a-22a59a92a0c4", "naam": "Utrecht"},
        )
        self.assertEqual(
            publication.informatie_categorieen,
            [{"uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597", "naam": "WOO"}],
        )
        self.assertEqual(
            publication.onderwerpen,
            [
                {
                    "uuid": "6deb195e-28d0-4d35-b267-418c9f30b772",
                    "officiele_titel": "GPP",
                }
            ],
        )
        self.assertEqual(
            publication.officiele_titel,
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        )
        self.assertEqual(
            publication.verkorte_titel, "Donec finibus non tortor quis sollicitudin."
        )
        self.assertEqual(
            publication.omschrijving,
            "Nulla at nisi at enim eleifend facilisis at vitae velit.",
        )
        # date -> converted to naive datetime
        self.assertEqual(
            publication.registratiedatum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
        )
        self.assertEqual(
            publication.laatst_gewijzigd_datum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
        )

        with self.subTest("re-indexing data with same UUID updates values"):
            index_publication(
                uuid=publication_uuid,
                publisher={
                    "uuid": "1a76e217-fbeb-48c5-a3c2-bde482aac2f0",
                    "naam": "Amsterdam",
                },
                informatie_categorieen=[
                    {"uuid": "587067ce-c2a7-45c3-a302-21650d0df0e1", "naam": "advies"},
                    {
                        "uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597",
                        "naam": "convenant",
                    },
                ],
                onderwerpen=[
                    {
                        "uuid": "6deb195e-28d0-4d35-b267-418c9f30b772",
                        "officiele_titel": "belasting",
                    },
                    {
                        "uuid": "bcb7f3be-93fa-4fdc-b4c8-a32354ee17dd",
                        "officiele_titel": "juridisch",
                    },
                ],
                officiele_titel="CHANGED TITLE",
                verkorte_titel="CHANGED",
                omschrijving="CHANGED OMSCHRIJVING.",
                registratiedatum=datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
                laatst_gewijzigd_datum=datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
            )
            with get_client() as client:
                updated_publication = Publication.get(
                    using=client,
                    id=publication_uuid,
                )

            assert isinstance(updated_publication, Publication), (
                "Expected doc to be indexed"
            )
            # Assert the provided data is indexed properly.
            self.assertEqual(
                updated_publication.uuid, "55b66c11-7cc9-4c50-bffa-7956e0edacef"
            )
            self.assertEqual(
                updated_publication.publisher,
                {"uuid": "1a76e217-fbeb-48c5-a3c2-bde482aac2f0", "naam": "Amsterdam"},
            )
            self.assertEqual(
                updated_publication.informatie_categorieen,
                [
                    {"uuid": "587067ce-c2a7-45c3-a302-21650d0df0e1", "naam": "advies"},
                    {
                        "uuid": "3c42a70a-d81d-4143-91d1-ebf62ac8b597",
                        "naam": "convenant",
                    },
                ],
            )
            self.assertEqual(
                updated_publication.onderwerpen,
                [
                    {
                        "uuid": "6deb195e-28d0-4d35-b267-418c9f30b772",
                        "officiele_titel": "belasting",
                    },
                    {
                        "uuid": "bcb7f3be-93fa-4fdc-b4c8-a32354ee17dd",
                        "officiele_titel": "juridisch",
                    },
                ],
            )
            self.assertEqual(updated_publication.officiele_titel, "CHANGED TITLE")
            self.assertEqual(updated_publication.verkorte_titel, "CHANGED")
            self.assertEqual(updated_publication.omschrijving, "CHANGED OMSCHRIJVING.")
            # date -> converted to naive datetime
            self.assertEqual(
                updated_publication.registratiedatum,
                datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
            )
            self.assertEqual(
                updated_publication.laatst_gewijzigd_datum,
                datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
            )


class TopicTaskTest(VCRMixin, ElasticSearchTestCase):
    def test_index_topic_roundtrip(self):
        topic_uuid = "d6787e70-0577-4c20-bb3a-1a67d92626a9"

        index_topic(
            uuid=topic_uuid,
            officiele_titel="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            omschrijving="Nulla at nisi at enim eleifend facilisis at vitae velit.",
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
        )

        # verify that it's indexed
        with get_client() as client:
            topic = Topic.get(
                using=client,
                id=topic_uuid,
            )

        # helps with type narrowing :)
        assert isinstance(topic, Topic), "Expected topic to be indexed"
        # Assert the provided data is indexed properly.
        self.assertEqual(topic.uuid, topic_uuid)
        self.assertEqual(
            topic.officiele_titel,
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        )
        self.assertEqual(
            topic.omschrijving,
            "Nulla at nisi at enim eleifend facilisis at vitae velit.",
        )
        # date -> converted to naive datetime
        self.assertEqual(
            topic.registratiedatum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
        )
        self.assertEqual(
            topic.laatst_gewijzigd_datum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=UTC),
        )

        with self.subTest("re-indexing data with same UUID updates values"):
            index_topic(
                uuid=topic_uuid,
                officiele_titel="CHANGED TITLE",
                omschrijving="CHANGED OMSCHRIJVING.",
                registratiedatum=datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
                laatst_gewijzigd_datum=datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
            )
            with get_client() as client:
                updated_topic = Topic.get(
                    using=client,
                    id=topic_uuid,
                )

            assert isinstance(updated_topic, Topic), "Expected topic to be indexed"
            # Assert the provided data is indexed properly.
            self.assertEqual(updated_topic.uuid, topic_uuid)
            self.assertEqual(updated_topic.officiele_titel, "CHANGED TITLE")
            self.assertEqual(updated_topic.omschrijving, "CHANGED OMSCHRIJVING.")
            # date -> converted to naive datetime
            self.assertEqual(
                updated_topic.registratiedatum,
                datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
            )
            self.assertEqual(
                updated_topic.laatst_gewijzigd_datum,
                datetime(2030, 1, 5, 12, 0, 0, tzinfo=UTC),
            )


class RemoveFromIndexTaskTests(VCRMixin, ElasticSearchTestCase):
    def test_remove_non_existing_document(self):
        result = remove_document_from_index("dd2635a9-228f-4cda-9bec-66310ccbb6a1")

        self.assertIsNone(result)

    def test_remove_indexed_document(self):
        doc = IndexDocumentFactory.build(uuid="ad4d66a8-1503-4743-ae55-d1765512530c")
        index_document(**doc)

        result = remove_document_from_index("ad4d66a8-1503-4743-ae55-d1765512530c")

        self.assertIsNone(result)
        with (
            get_client() as client,
            self.assertRaises(NotFoundError),
        ):
            Document.get(id="ad4d66a8-1503-4743-ae55-d1765512530c", using=client)

    def test_remove_non_existing_publication(self):
        result = remove_publication_from_index("dd2635a9-228f-4cda-9bec-66310ccbb6a1")

        self.assertIsNone(result)

    def test_remove_indexed_publication(self):
        pub = IndexPublicationFactory.build(uuid="ad4d66a8-1503-4743-ae55-d1765512530c")
        index_publication(**pub)

        result = remove_publication_from_index("ad4d66a8-1503-4743-ae55-d1765512530c")

        self.assertIsNone(result)
        with (
            get_client() as client,
            self.assertRaises(NotFoundError),
        ):
            Publication.get(id="ad4d66a8-1503-4743-ae55-d1765512530c", using=client)

    def test_remove_non_existing_topic(self):
        result = remove_topic_from_index("5c640122-843d-4352-b53a-8a405341521c")

        self.assertIsNone(result)

    def test_remove_indexed_topic(self):
        topic = IndexTopicFactory.build(uuid="177e5bac-bdc1-4aff-b4de-96eedd8753e6")
        index_topic(**topic)

        result = remove_topic_from_index("177e5bac-bdc1-4aff-b4de-96eedd8753e6")

        self.assertIsNone(result)
        with (
            get_client() as client,
            self.assertRaises(NotFoundError),
        ):
            Topic.get(id="177e5bac-bdc1-4aff-b4de-96eedd8753e6", using=client)
