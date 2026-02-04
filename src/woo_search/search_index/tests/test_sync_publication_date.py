from datetime import UTC, datetime

from django.core.management import call_command

from woo_search.api.tests.mixin import TokenAuthMixin
from woo_search.search_index.client import get_client
from woo_search.utils.tests.vcr import VCRMixin

from ..index import Document, Publication, Topic
from ..tasks import index_document, index_publication
from .base import ElasticSearchAPITestCase
from .factories import IndexDocumentFactory, IndexPublicationFactory


class SyncPublicationDateCommandTestCase(
    TokenAuthMixin, VCRMixin, ElasticSearchAPITestCase
):
    def test_update_empty_publication_date(self):
        pub = IndexPublicationFactory.build(
            uuid="83ec1da4-bb76-43bc-ac0a-857acf9b4541",
            gepubliceerd_op=None,
            registratiedatum=datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
        )
        doc = IndexDocumentFactory.build(
            uuid="fe208e6b-c2e7-4192-a4ab-82f438416e82",
            gepubliceerd_op=None,
            registratiedatum=datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
        )
        index_publication(**pub)
        index_document(**doc)

        # indexing the topics manually because we do some magic during the indexing task
        topic = {
            "uuid": "bfb07018-86d9-45a0-a9f0-9f9ff67e7e20",
            "officieleTitel": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
            "registratiedatum": datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
            "laatstGewijzigdDatum": datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
        }
        with get_client() as client:
            client.index(
                index="topic", id="bfb07018-86d9-45a0-a9f0-9f9ff67e7e20", document=topic
            )

        call_command(
            "sync_publication_date",
            verbosity=0,
        )

        with get_client() as client:
            pub = Publication.get(
                using=client, id="83ec1da4-bb76-43bc-ac0a-857acf9b4541"
            )
            assert pub is not None
            self.assertEqual(
                pub.gepubliceerd_op,
                datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
            )
            doc = Document.get(using=client, id="fe208e6b-c2e7-4192-a4ab-82f438416e82")
            assert doc is not None
            self.assertEqual(
                doc.gepubliceerd_op,
                datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
            )
            topic = Topic.get(using=client, id="bfb07018-86d9-45a0-a9f0-9f9ff67e7e20")
            assert topic is not None
            self.assertEqual(
                topic.gepubliceerd_op,
                datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
            )

    def test_update_set_publication_date_does_not_update(self):
        pub = IndexPublicationFactory.build(
            uuid="83ec1da4-bb76-43bc-ac0a-857acf9b4541",
            gepubliceerd_op=datetime(2026, 1, 1, 1, 1, 1, tzinfo=UTC),
            registratiedatum=datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
        )
        doc = IndexDocumentFactory.build(
            uuid="fe208e6b-c2e7-4192-a4ab-82f438416e82",
            gepubliceerd_op=datetime(2026, 1, 1, 1, 1, 1, tzinfo=UTC),
            registratiedatum=datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
        )

        index_publication(**pub)
        index_document(**doc)

        # indexing the topics manually because we do some magic during the indexing task
        topic = {
            "uuid": "bfb07018-86d9-45a0-a9f0-9f9ff67e7e20",
            "officieleTitel": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
            ),
            "omschrijving": "Nulla at nisi at enim eleifend facilisis at vitae velit.",
            "registratiedatum": datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
            "gepubliceerd_op": datetime(2026, 1, 1, 1, 1, 1, tzinfo=UTC),
            "laatstGewijzigdDatum": datetime(2025, 1, 1, 1, 1, 1, tzinfo=UTC),
        }
        with get_client() as client:
            client.index(
                index="topic", id="bfb07018-86d9-45a0-a9f0-9f9ff67e7e20", document=topic
            )

        call_command(
            "sync_publication_date",
            verbosity=0,
        )

        with get_client() as client:
            pub = Publication.get(
                using=client, id="83ec1da4-bb76-43bc-ac0a-857acf9b4541"
            )
            assert pub is not None
            self.assertEqual(
                pub.gepubliceerd_op,
                datetime(2026, 1, 1, 1, 1, 1, tzinfo=UTC),
            )
            doc = Document.get(using=client, id="fe208e6b-c2e7-4192-a4ab-82f438416e82")
            assert doc is not None
            self.assertEqual(
                doc.gepubliceerd_op,
                datetime(2026, 1, 1, 1, 1, 1, tzinfo=UTC),
            )
            topic = Topic.get(using=client, id="bfb07018-86d9-45a0-a9f0-9f9ff67e7e20")
            assert topic is not None
            self.assertEqual(
                topic.gepubliceerd_op,
                datetime(2026, 1, 1, 1, 1, 1, tzinfo=UTC),
            )
