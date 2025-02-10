from django.core.management import BaseCommand, CommandError

from elastic_transport import ConnectionError
from elasticsearch import ApiError

from ...client import get_client
from ...utils import get_index_document_types


class Command(BaseCommand):
    help = "Initialize Elastic Search mappings"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--wait",
            "--wait-until-healthy",
            dest="wait_until_healthy",
            action="store_true",
            help="Wait for the cluster to report itself as healthy before doing anything.",
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

            if options["wait_until_healthy"]:
                if verbosity >= 1:
                    self.stdout.write("Waiting for cluster...", ending=" ")
                try:
                    # single node clusters are always yellow
                    health = client.cluster.health(wait_for_status="yellow")
                except (ConnectionError, ApiError) as exc:
                    raise CommandError("Could not connect to cluster") from exc
                else:
                    status = health["status"]
                    if verbosity >= 1:
                        self.stdout.write(" [OK]", self.style.SUCCESS, ending="")
                        self.stdout.write(f" (status: {status})")

            for doc_type in get_index_document_types():
                if verbosity >= 1:
                    self.stdout.write(
                        f"  Initializing index & mappings '{doc_type.Index.name}' for "
                        f"{doc_type}...",
                        self.style.MIGRATE_LABEL,
                        ending="",
                    )

                doc_type.init(using=client)

                if verbosity >= 1:
                    self.stdout.write(" [OK]", self.style.SUCCESS)
