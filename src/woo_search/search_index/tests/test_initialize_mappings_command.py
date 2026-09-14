from unittest.mock import MagicMock, patch

from django.core.management import CommandError
from django.test import SimpleTestCase

from elastic_transport import (
    ApiResponseMeta,
    ConnectionError,
    ConnectionTimeout,
    HttpHeaders,
    NodeConfig,
)
from elasticsearch import ApiError

from ..management.commands import initialize_mappings


def _api_error(status: int) -> ApiError:
    meta = ApiResponseMeta(
        status=status,
        http_version="1.1",
        headers=HttpHeaders(),
        duration=0.0,
        node=NodeConfig(scheme="http", host="localhost", port=9200),
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

    def test_gives_up_while_master_is_never_elected(self):
        client = _client(health=_api_error(503))
        # exhaust the deadline on the second pass through the loop
        with patch.object(
            initialize_mappings.time, "monotonic", side_effect=[0, 0, 60]
        ):
            with patch.object(initialize_mappings.time, "sleep") as mock_sleep:
                health = initialize_mappings._wait_for_cluster(client, timeout=60)

        self.assertIsNone(health)
        self.assertEqual(_health_calls(client).call_count, 2)
        self.assertEqual(mock_sleep.call_count, 1)

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


class WaitArgumentTests(SimpleTestCase):
    """
    ``--wait`` takes an optional budget, so that a deployment can grant a slow
    cluster more than the default without a second, separate option.
    """

    def _parse(self, *argv: str) -> int:
        parser = initialize_mappings.Command().create_parser(
            "manage.py", "initialize_mappings"
        )
        return vars(parser.parse_args(list(argv)))["wait_until_healthy"]

    def test_without_the_flag_nothing_is_waited_for(self):
        self.assertEqual(self._parse(), 0)

    def test_bare_flag_uses_the_default_budget(self):
        self.assertEqual(
            self._parse("--wait"), initialize_mappings.DEFAULT_WAIT_TIMEOUT
        )

    def test_flag_accepts_an_explicit_budget(self):
        self.assertEqual(self._parse("--wait", "300"), 300)

    def test_long_alias_still_works(self):
        # bin/docker_start.sh and existing deployments use both spellings
        self.assertEqual(self._parse("--wait-until-healthy", "300"), 300)

    def test_following_option_is_not_swallowed_as_the_budget(self):
        parser = initialize_mappings.Command().create_parser(
            "manage.py", "initialize_mappings"
        )
        options = vars(parser.parse_args(["--wait", "--verbosity", "0"]))

        self.assertEqual(options["wait_until_healthy"], 60)
        self.assertEqual(options["verbosity"], 0)
