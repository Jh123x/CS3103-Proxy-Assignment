import requests
import unittest

from .constants import CONTROL_URL, TEST_URL


class TestSanityCheck(unittest.TestCase):
    """Test the default setup of the Proxy"""

    def test_default_fetch(self) -> None:
        resp2 = requests.get(CONTROL_URL)
        self.assertEqual(resp2.status_code, 200)

    def test_run_default_test_cases(self) -> None:
        for url in TEST_URL:
            resp2 = requests.get(url)
            self.assertEqual(resp2.status_code, 200)

if __name__ == "__main__":
    unittest.main()
