from datetime import date, datetime, timezone

from woo_search.utils.date import TIMEZONE_AMS
from woo_search.utils.tests.vcr import VCRMixin

from ..client import get_client
from ..documents import Document, Publication
from ..tasks import index_document, index_publication
from .base import ElasticSearchTestCase


class DocumentTaskTest(VCRMixin, ElasticSearchTestCase):
    def test_index_document_roundtrip(self):
        document_uuid = "0095704d-4216-4de3-83d2-20dba551b0dc"

        index_document(
            uuid=document_uuid,
            publicatie="d481bea6-335b-4d90-9b27-ac49f7196633",
            publisher={
                "uuid": "f8b2b355-1d6e-4c1a-ba18-565f422997da",
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
        self.assertEqual(
            doc.creatiedatum, datetime(2026, 1, 1, 0, 0, 0, tzinfo=TIMEZONE_AMS)
        )
        self.assertEqual(
            doc.registratiedatum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            doc.laatst_gewijzigd_datum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )

        with self.subTest("re-indexing data with same UUID updates values"):
            index_document(
                uuid=document_uuid,
                publicatie="CHANGED",
                publisher={
                    "uuid": "CHANGED",
                    "naam": "Amsterdam",
                },
                identifier="https://www.example.com/999",
                officiele_titel="CHANGED TITLE",
                verkorte_titel="CHANGED",
                omschrijving="CHANGED OMSCHRIJVING",
                creatiedatum=date(2030, 1, 1),
                registratiedatum=datetime(2030, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
                laatst_gewijzigd_datum=datetime(
                    2030, 1, 5, 12, 0, 0, tzinfo=timezone.utc
                ),
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
            self.assertEqual(
                updated_doc.creatiedatum,
                datetime(2030, 1, 1, 0, 0, 0, tzinfo=TIMEZONE_AMS),
            )
            self.assertEqual(
                updated_doc.registratiedatum,
                datetime(2030, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            )
            self.assertEqual(
                updated_doc.laatst_gewijzigd_datum,
                datetime(2030, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            )


class PublicationTaskTest(VCRMixin, ElasticSearchTestCase):
    def test_index_document_roundtrip(self):
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
            officiele_titel="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            verkorte_titel="Donec finibus non tortor quis sollicitudin.",
            omschrijving="Nulla at nisi at enim eleifend facilisis at vitae velit.",
            registratiedatum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            laatst_gewijzigd_datum=datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
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
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            publication.laatst_gewijzigd_datum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
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
                officiele_titel="CHANGED TITLE",
                verkorte_titel="CHANGED",
                omschrijving="CHANGED OMSCHRIJVING.",
                registratiedatum=datetime(2030, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
                laatst_gewijzigd_datum=datetime(
                    2030, 1, 5, 12, 0, 0, tzinfo=timezone.utc
                ),
            )

            with get_client() as client:
                updated_publication = Publication.get(
                    using=client,
                    id=publication_uuid,
                )

            assert isinstance(
                updated_publication, Publication
            ), "Expected doc to be indexed"
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
            self.assertEqual(updated_publication.officiele_titel, "CHANGED TITLE")
            self.assertEqual(updated_publication.verkorte_titel, "CHANGED")
            self.assertEqual(updated_publication.omschrijving, "CHANGED OMSCHRIJVING.")
            # date -> converted to naive datetime
            self.assertEqual(
                updated_publication.registratiedatum,
                datetime(2030, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            )
            self.assertEqual(
                updated_publication.laatst_gewijzigd_datum,
                datetime(2030, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
            )
