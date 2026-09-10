from unittest.mock import MagicMock, patch

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase

from ..management.commands import initialize_mappings


class InitializeMappingsConnectionTests(SimpleTestCase):
    """
    A cluster that cannot be reached must be an error, not a silent no-op.

    The command runs as an init container or as a Job alongside the cluster it
    talks to, so "not reachable yet" is a normal condition - but reporting
    success without creating the indices leaves the deployment believing the
    index exists.
    """

    def test_connection_failure_raises_command_error(self):
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.ping.return_value = False

        with patch.object(initialize_mappings, "get_client", return_value=client):
            with self.assertRaises(CommandError) as ctx:
                call_command("initialize_mappings", verbosity=0)

        self.assertIn("Could not connect", str(ctx.exception))
        self.assertEqual(client.ping.call_count, 1)

    def test_connect_without_wait_pings_once(self):
        client = MagicMock()
        client.ping.return_value = False

        connected = initialize_mappings._connect(client, wait=False, timeout=60)

        self.assertFalse(connected)
        self.assertEqual(client.ping.call_count, 1)

    def test_connect_with_wait_retries_until_available(self):
        client = MagicMock()
        client.ping.side_effect = [False, False, True]

        with patch.object(initialize_mappings.time, "sleep") as mock_sleep:
            connected = initialize_mappings._connect(client, wait=True, timeout=60)

        self.assertTrue(connected)
        self.assertEqual(client.ping.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    def test_connect_with_wait_gives_up_after_timeout(self):
        client = MagicMock()
        client.ping.return_value = False

        with patch.object(initialize_mappings.time, "sleep") as mock_sleep:
            connected = initialize_mappings._connect(client, wait=True, timeout=0)

        self.assertFalse(connected)
        self.assertEqual(client.ping.call_count, 1)
        mock_sleep.assert_not_called()
