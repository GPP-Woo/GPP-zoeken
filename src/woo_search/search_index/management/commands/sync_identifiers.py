from django.core.management import BaseCommand

from elasticsearch_dsl import UpdateByQuery

from ...client import get_client
from ...index import Document


class Command(BaseCommand):
    help = (
        "Fill in the empty document identifiers with the "
        "filled in identifier value of the document."
    )

    def handle(self, **options):  # pragma: no cover
        verbosity = options["verbosity"]

        with get_client() as client:
            if verbosity >= 1:
                self.stdout.write("Pinging cluster...", ending=" ")

            connected = client.ping()
            if not connected:
                self.stdout.write("")
                self.stderr.write(
                    "Could not connect to configured Elastic Search host!"
                )
                return

            if verbosity >= 1:
                self.stdout.write("Cluster online.", self.style.SUCCESS)

            ubq = UpdateByQuery().doc_type(Document)

            ubq = ubq.from_dict(
                {
                    "query": {
                        "bool": {"must_not": [{"exists": {"field": "identifiers"}}]}
                    }
                }
            )
            ubq = ubq.script(source="ctx._source.identifiers=[ctx._source.identifier]")

            ubq = ubq.using(client)
            # manually set it because using it with .index doesn't set _index properly
            ubq._index = Document.Index.name  # pyright: ignore[reportAttributeAccessIssue]
            response = ubq.execute()

            if verbosity >= 1:
                if response.updated >= 1:
                    self.stdout.write(
                        f"Synced {response.updated} documents", self.style.SUCCESS
                    )
                else:
                    self.stderr.write(" [Error]", self.style.ERROR)
