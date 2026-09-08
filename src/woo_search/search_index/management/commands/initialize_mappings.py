import time

from django.core.management import BaseCommand, CommandError

from elastic_transport import ConnectionError
from elasticsearch import ApiError, Elasticsearch

from ...client import get_client
from ...constants import DOCUMENT_ATTACHMENT_PIPELINE_ID
from ...ingest import setup_document_attachment_processor
from ...utils import get_index_document_types

DEFAULT_CONNECT_TIMEOUT = 60
"""
Seconds to keep retrying the initial connection when ``--wait`` is passed.

Matches the timeout ``bin/docker_start.sh`` uses with ``wait_for_it.sh`` for the
same purpose.
"""

CONNECT_RETRY_INTERVAL = 1


def _connect(client: Elasticsearch, *, wait: bool, timeout: int) -> bool:
    """
    Ping the cluster, optionally retrying until it becomes available.

    Without ``wait`` this is a single ping. With ``wait``, the ping is retried
    until ``timeout`` seconds have passed - a cluster that is still starting up
    is the normal case when this runs as an init container or a Job created in
    the same breath as the cluster itself.
    """
    if not wait:
        return client.ping()

    deadline = time.monotonic() + timeout
    while True:
        if client.ping():
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(CONNECT_RETRY_INTERVAL)


class Command(BaseCommand):
    help = "Initialize Elastic Search mappings"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--wait",
            "--wait-until-healthy",
            dest="wait_until_healthy",
            action="store_true",
            help=(
                "Wait for the cluster to become available and report itself as "
                "healthy before doing anything."
            ),
        )
        parser.add_argument(
            "--connect-timeout",
            type=int,
            default=DEFAULT_CONNECT_TIMEOUT,
            help=(
                "How long to keep retrying the initial connection, in seconds. "
                "Only used together with --wait. Defaults to "
                f"{DEFAULT_CONNECT_TIMEOUT}."
            ),
        )

    def handle(self, **options):  # pragma: no cover
        verbosity = options["verbosity"]
        with get_client() as client:
            if verbosity >= 1:
                self.stdout.write("Pinging cluster...", ending=" ")

            connected = _connect(
                client,
                wait=options["wait_until_healthy"],
                timeout=options["connect_timeout"],
            )
            if not connected:
                self.stdout.write("")
                raise CommandError(
                    "Could not connect to configured Elastic Search host!"
                )

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

            self.stdout.write(
                "  Initializing ingest pipelines "
                f"'{DOCUMENT_ATTACHMENT_PIPELINE_ID}'...",
                self.style.MIGRATE_LABEL,
                ending="",
            )

            if setup_document_attachment_processor(client):
                self.stdout.write(" [OK]", self.style.SUCCESS)
            else:
                self.stderr.write(" [Error]", self.style.ERROR)
