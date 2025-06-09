import unittest
from unittest.mock import patch
from click.testing import CliRunner

from cli.commands.check_backends import check_backends

class TestCheckBackendsCommand(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @patch('cli.commands.check_backends.check_backend_availability')
    def test_check_backends_all_available(self, mock_check_backend_availability):
        mock_check_backend_availability.return_value = {
            "backend1": True,
            "backend2": True
        }
        result = self.runner.invoke(check_backends)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("backend1: Available", result.output)
        self.assertIn("backend2: Available", result.output)
        self.assertNotIn("No chord extraction backends available.", result.output)

    @patch('cli.commands.check_backends.check_backend_availability')
    def test_check_backends_none_available(self, mock_check_backend_availability):
        mock_check_backend_availability.return_value = {
            "backend1": False,
            "backend2": False
        }
        result = self.runner.invoke(check_backends)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("backend1: Unavailable", result.output)
        self.assertIn("backend2: Unavailable", result.output)
        self.assertIn("No chord extraction backends available. See README for setup instructions.", result.output)

    @patch('cli.commands.check_backends.check_backend_availability')
    def test_check_backends_mixed_availability(self, mock_check_backend_availability):
        mock_check_backend_availability.return_value = {
            "backend1": True,
            "backend2": False
        }
        result = self.runner.invoke(check_backends)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("backend1: Available", result.output)
        self.assertIn("backend2: Unavailable", result.output)
        self.assertNotIn("No chord extraction backends available.", result.output)

if __name__ == '__main__':
    unittest.main()
