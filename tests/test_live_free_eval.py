import unittest
from unittest.mock import patch

from scripts.run_live_free_eval import main


class LegacyOpenRouterEntryPointTests(unittest.TestCase):
    def test_refuses_before_credentials_network_or_artifact(self):
        with (
            patch("scripts.run_live_free_eval.load_root_env") as credentials,
            patch("scripts.run_live_free_eval.urlopen") as network,
            patch("scripts.run_live_free_eval.write_evidence", create=True) as evidence,
        ):
            self.assertEqual(main(), 2)
        credentials.assert_not_called()
        network.assert_not_called()
        evidence.assert_not_called()
