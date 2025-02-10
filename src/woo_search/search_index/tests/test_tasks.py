import uuid
from datetime import datetime, timezone

from woo_search.utils.tests.vcr import VCRMixin

from ..client import get_client
from ..documents import Document
from ..tasks import save_document
from .base import ElasticSearchTestCase


class DocumentTaskTest(VCRMixin, ElasticSearchTestCase):
    elastic_documents = (Document,)

    def test_index_document_roundtrip(self):
        document_uuid = uuid.UUID("0095704d-4216-4de3-83d2-20dba551b0dc")

        data = {
            "id": document_uuid,
            "uuid": document_uuid,
            "publicatie": uuid.UUID("d481bea6-335b-4d90-9b27-ac49f7196633"),
            "publisher": uuid.UUID("f8b2b355-1d6e-4c1a-ba18-565f422997da"),
            "identifier": "https://www.example.com/1",
            "officiele_titel": "A test document",
            "verkorte_titel": "A document",
            "omschrijving": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "creatiedatum": "2026-01-01",
            "registratiedatum": "2026-01-05T12:00:00.000000+00:00",
            "laatst_gewijzigd_datum": "2026-01-05T13:00:00.000000+01:00",
        }

        save_document(data)

        # verify that it's indexed
        with get_client() as client:
            doc = Document.get(
                using=client,
                id="0095704d-4216-4de3-83d2-20dba551b0dc",
            )

        # helps with type narrowing :)
        assert isinstance(doc, Document), "Expected doc to be indexed"
        # Assert the provided data is indexed properly.
        self.assertEqual(doc.uuid, "0095704d-4216-4de3-83d2-20dba551b0dc")
        self.assertEqual(doc.publicatie, "d481bea6-335b-4d90-9b27-ac49f7196633")
        self.assertEqual(doc.publisher, "f8b2b355-1d6e-4c1a-ba18-565f422997da")
        self.assertEqual(doc.identifier, "https://www.example.com/1")
        self.assertEqual(doc.officiele_titel, "A test document")
        self.assertEqual(doc.verkorte_titel, "A document")
        self.assertEqual(
            doc.omschrijving, "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        )
        # date -> converted to naive datetime
        self.assertEqual(doc.creatiedatum, datetime(2026, 1, 1, 0, 0))
        self.assertEqual(
            doc.registratiedatum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(
            doc.laatst_gewijzigd_datum,
            datetime(2026, 1, 5, 12, 0, 0, tzinfo=timezone.utc),
        )
