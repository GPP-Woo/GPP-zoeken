from django.core.management import call_command

from woo_search.api.tests.mixin import TokenAuthMixin
from woo_search.search_index.client import get_client
from woo_search.utils.tests.vcr import VCRMixin

from ..index import Document
from ..tasks import index_document
from .base import ElasticSearchAPITestCase
from .factories import IndexDocumentFactory


class SyncIdentifiersCommandTestCase(
    TokenAuthMixin, VCRMixin, ElasticSearchAPITestCase
):
    def test_update_empty_identifiers(self):
        doc1 = IndexDocumentFactory.build(
            uuid="af9fb832-1fd7-4ca1-885f-3588bdbb3984",
            identifiers=[],
            identifier="foo",
        )
        doc2 = IndexDocumentFactory.build(
            uuid="1761cf3a-72ba-4145-94c2-7b5c0ed3cc67",
            identifiers=[],
            identifier="bar",
        )
        index_document(**doc1)
        index_document(**doc2)

        call_command(
            "sync_identifiers",
            verbosity=0,
        )

        with get_client() as client:
            doc = Document.get(using=client, id="af9fb832-1fd7-4ca1-885f-3588bdbb3984")
            assert doc is not None
            self.assertEqual(doc.identifiers, ["foo"])

            doc2 = Document.get(using=client, id="1761cf3a-72ba-4145-94c2-7b5c0ed3cc67")
            assert doc2 is not None
            self.assertEqual(doc2.identifiers, ["bar"])

    def test_update_set_identifiers_does_not_update(self):
        doc1 = IndexDocumentFactory.build(
            uuid="af9fb832-1fd7-4ca1-885f-3588bdbb3984",
            identifiers=["identifier-1"],
            identifier="foo",
        )
        doc2 = IndexDocumentFactory.build(
            uuid="1761cf3a-72ba-4145-94c2-7b5c0ed3cc67",
            identifiers=["identifier-2"],
            identifier="bar",
        )
        index_document(**doc1)
        index_document(**doc2)

        call_command(
            "sync_identifiers",
            verbosity=0,
        )

        with get_client() as client:
            doc = Document.get(using=client, id="af9fb832-1fd7-4ca1-885f-3588bdbb3984")
            assert doc is not None
            self.assertEqual(doc.identifiers, ["identifier-1"])

            doc2 = Document.get(using=client, id="1761cf3a-72ba-4145-94c2-7b5c0ed3cc67")
            assert doc2 is not None
            self.assertEqual(doc2.identifiers, ["identifier-2"])
