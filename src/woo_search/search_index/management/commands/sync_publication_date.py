from django.core.management import BaseCommand

from elasticsearch_dsl import UpdateByQuery

from ...client import get_client
from ...index import Document, Publication, Topic


class Command(BaseCommand):
    help = "Fill the empty publication date with the old registration date."

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

            ubq = UpdateByQuery().doc_type(Document, Publication, Topic)

            ubq = ubq.from_dict(
                {
                    "query": {
                        "bool": {"must_not": [{"exists": {"field": "gepubliceerd_op"}}]}
                    }
                }
            )
            ubq = ubq.script(
                source="ctx._source.gepubliceerd_op=ctx._source.registratiedatum"
            )

            ubq = ubq.using(client)
            ubq._index = (Publication.Index.name, Document.Index.name, Topic.Index.name)  # pyright: ignore[reportAttributeAccessIssue]
            response = ubq.execute()

            if verbosity >= 1:
                if response.updated >= 1:
                    self.stdout.write(
                        f"Synced {response.updated} es documents", self.style.SUCCESS
                    )
                else:
                    self.stderr.write(" [Error]", self.style.ERROR)
