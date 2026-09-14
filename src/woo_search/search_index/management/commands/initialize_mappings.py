import math
import time
from typing import Any

from django.core.management import BaseCommand, CommandError

from elastic_transport import ConnectionError, ConnectionTimeout, ObjectApiResponse
from elasticsearch import ApiError, Elasticsearch

from ...client import get_client
from ...constants import DOCUMENT_ATTACHMENT_PIPELINE_ID
from ...ingest import setup_document_attachment_processor
from ...utils import get_index_document_types

DEFAULT_WAIT_TIMEOUT = 60
"Seconds to wait for the cluster to become healthy when ``--wait`` is passed."

CONNECT_RETRY_INTERVAL = 1
"Seconds between attempts while Elastic Search is not answering yet."


def _wait_for_cluster(
    client: Elasticsearch, *, timeout: int
) -> ObjectApiResponse[Any] | None:
    """
    Wait for the cluster to become healthy, returning its health or ``None``.

    ``cluster.health(timeout=...)`` is a *server side* wait: Elastic Search holds
    the request open until the requested status is reached. That only helps once
    it answers HTTP at all - running as an init container, or as a Job created in
    the same breath as the cluster itself, we are typically up before it is, so
    the errors from that window are retried here against the same deadline.

    ``timeout`` is the entire budget, however it ends up divided between "not
    listening yet" and "not healthy yet". A timeout of ``0`` checks once.
    """
    deadline = time.monotonic() + timeout
    while True:
        remaining = max(math.ceil(deadline - time.monotonic()), 0)
        try:
            health = client.options(
                # ES signals ``timed_out`` with 408
                ignore_status=408,
                # must outlast the wait it asks for
                request_timeout=remaining + CONNECT_RETRY_INTERVAL,
            ).cluster.health(
                # single node clusters never reach green
                wait_for_status="yellow",
                timeout=f"{remaining}s",
            )
        except (ConnectionError, ConnectionTimeout):
            # nothing is answering yet - keep trying until the budget is spent
            if not remaining:
                return None
            time.sleep(CONNECT_RETRY_INTERVAL)
        except ApiError as exc:
            # expect 503 during startup master election
            if exc.status_code != 503:
                raise CommandError(
                    f"Elastic Search returned an unexpected error: {exc}"
                ) from exc
            if not remaining:
                return None
            time.sleep(CONNECT_RETRY_INTERVAL)
        else:
            return None if health["timed_out"] else health


class Command(BaseCommand):
    help = "Initialize Elastic Search mappings"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--wait",
            "--wait-until-healthy",
            dest="wait_until_healthy",
            type=int,
            nargs="?",
            const=DEFAULT_WAIT_TIMEOUT,
            default=0,
            help=(
                "Wait for the cluster to become healthy before executing. "
                "Optionally accepts a timeout in seconds (defaults to "
                f"{DEFAULT_WAIT_TIMEOUT})."
            ),
        )

    def handle(self, **options):  # pragma: no cover
        verbosity = options["verbosity"]
        timeout = options["wait_until_healthy"]
        with get_client() as client:
            if verbosity >= 1:
                label = "Waiting for cluster" if timeout else "Checking cluster"
                self.stdout.write(f"{label}...", ending=" ")

            health = _wait_for_cluster(client, timeout=timeout)
            if health is None:
                self.stdout.write("")
                raise CommandError(
                    "Elastic Search cluster did not become healthy in time!"
                )

            if verbosity >= 1:
                self.stdout.write("[OK]", self.style.SUCCESS, ending="")
                self.stdout.write(f" (status: {health['status']})")

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
