from datetime import date, datetime, timezone

from woo_search.utils.date import TIMEZONE_AMS
from woo_search.utils.tests.vcr import VCRMixin

from ..client import get_client
from ..documents import Document
from ..tasks import index_document
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
