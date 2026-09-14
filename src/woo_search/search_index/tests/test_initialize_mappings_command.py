from unittest.mock import MagicMock, patch

from django.core.management import CommandError
from django.test import SimpleTestCase

from elastic_transport import ApiResponseMeta, ConnectionError, ConnectionTimeout
from elasticsearch import ApiError

from ..management.commands import initialize_mappings


def _api_error(status: int) -> ApiError:
    meta = ApiResponseMeta(
        status=status, http_version="1.1", headers={}, duration=0.0, node=None
    )
    return ApiError(f"boom ({status})", meta=meta, body={})


def _client(*, health) -> MagicMock:
    """
    Build a client whose ``options(...).cluster.health(...)`` behaves as given.
    """
    client = MagicMock()
    client.options.return_value.cluster.health.side_effect = health
    return client


def _health_calls(client: MagicMock) -> MagicMock:
    return client.options.return_value.cluster.health


class WaitForClusterTests(SimpleTestCase):
    """
    A cluster that cannot be reached must be an error, not a silent no-op.

    The command runs as an init container or as a Job alongside the cluster it
    talks to, so "not reachable yet" is a normal condition - but reporting
    success without creating the indices leaves the deployment believing the
    index exists.
    """

    def test_healthy_cluster_returns_health(self):
        client = _client(health=[{"status": "yellow", "timed_out": False}])

        health = initialize_mappings._wait_for_cluster(client, timeout=60)

        assert health is not None
        self.assertEqual(health["status"], "yellow")
        self.assertEqual(_health_calls(client).call_count, 1)

    def test_server_side_wait_expiring_is_a_failure(self):
        # ES answers 408 when the wait expires, which ``ignore_status`` turns
        # back into a body with ``timed_out`` set.
        client = _client(health=[{"status": "red", "timed_out": True}])

        self.assertIsNone(initialize_mappings._wait_for_cluster(client, timeout=60))

    def test_no_timeout_checks_once_without_sleeping(self):
        client = _client(health=[ConnectionError("refused")])

        with patch.object(initialize_mappings.time, "sleep") as mock_sleep:
            health = initialize_mappings._wait_for_cluster(client, timeout=0)

        self.assertIsNone(health)
        self.assertEqual(_health_calls(client).call_count, 1)
        mock_sleep.assert_not_called()

    def test_retries_while_cluster_is_not_answering_yet(self):
        # the window before ES accepts connections at all - a server side
        # timeout cannot cover it, because the request never arrives
        client = _client(
            health=[
                ConnectionError("refused"),
                ConnectionTimeout("no route"),
                {"status": "yellow", "timed_out": False},
            ]
        )

        with patch.object(initialize_mappings.time, "sleep") as mock_sleep:
            health = initialize_mappings._wait_for_cluster(client, timeout=60)

        assert health is not None
        self.assertEqual(health["status"], "yellow")
        self.assertEqual(_health_calls(client).call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    def test_retries_while_master_is_not_elected_yet(self):
        client = _client(
            health=[_api_error(503), {"status": "yellow", "timed_out": False}]
        )

        with patch.object(initialize_mappings.time, "sleep"):
            health = initialize_mappings._wait_for_cluster(client, timeout=60)

        assert health is not None
        self.assertEqual(_health_calls(client).call_count, 2)

    def test_unexpected_api_error_fails_immediately(self):
        # bad credentials are not going to fix themselves by waiting
        client = _client(health=[_api_error(401)])

        with self.assertRaises(CommandError) as ctx:
            initialize_mappings._wait_for_cluster(client, timeout=60)

        self.assertIn("unexpected error", str(ctx.exception))
        self.assertEqual(_health_calls(client).call_count, 1)

    def test_gives_up_once_the_budget_is_spent(self):
        client = _client(health=ConnectionError("refused"))
        # exhaust the deadline on the second pass through the loop
        with patch.object(
            initialize_mappings.time, "monotonic", side_effect=[0, 0, 60]
        ):
            with patch.object(initialize_mappings.time, "sleep") as mock_sleep:
                health = initialize_mappings._wait_for_cluster(client, timeout=60)

        self.assertIsNone(health)
        self.assertEqual(_health_calls(client).call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)


class WaitForClusterRequestTests(SimpleTestCase):
    """
    The parameters handed to Elastic Search are load bearing, see #137.
    """

    def test_timeout_is_sent_as_a_duration_with_a_unit(self):
        # a bare int is rejected by ES: "failed to parse setting [timeout] with
        # value [60] as a time value: unit is missing or unrecognized"
        client = _client(health=[{"status": "yellow", "timed_out": False}])

        initialize_mappings._wait_for_cluster(client, timeout=60)

        _, kwargs = _health_calls(client).call_args
        self.assertEqual(kwargs["wait_for_status"], "yellow")
        self.assertEqual(kwargs["timeout"], "60s")

    def test_client_outlasts_the_server_side_wait_it_asks_for(self):
        # otherwise the client aborts with a ConnectionTimeout while ES is still
        # dutifully holding the request open
        client = _client(health=[{"status": "yellow", "timed_out": False}])

        initialize_mappings._wait_for_cluster(client, timeout=60)

        _, kwargs = client.options.call_args
        self.assertEqual(kwargs["ignore_status"], 408)
        self.assertGreater(kwargs["request_timeout"], 60)
