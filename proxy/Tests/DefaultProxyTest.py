import requests
import unittest
import socket
import multiprocessing as mp

from .constants import CONTROL_URL, TEST_URL, TEST_PORT
from .utils import proxy_stdout_bypass


class TestDefaultProxy(unittest.TestCase):
    """Test the default setup of the Proxy"""

    def setUp(self) -> None:
        self.port = TEST_PORT
        _, w = mp.Pipe()
        self.p = mp.Process(target=proxy_stdout_bypass, args=(self.port, 0, 0))
        self.p.start()
        self.proxies = {
            "http": f"127.0.0.1:{self.port}",
        }
        return super().setUp()

    def tearDown(self) -> None:
        self.p.terminate()
        return super().tearDown()

    def test_default_fetch(self) -> None:
        with requests.Session() as s:
            response = s.get(CONTROL_URL, proxies=self.proxies, timeout=3)
            self.assertEqual(response.status_code, 200)
            resp2 = requests.get(CONTROL_URL, timeout=3)

            assert response.content == resp2.content, (
                response.content + b"\n\n" + resp2.content
            )

    def test_run_default_test_cases(self) -> None:
        for url in TEST_URL:
            try:
                response = requests.get(url, proxies=self.proxies, timeout=3)
            except Exception as e:
                assert False, f"Failed to fetch {url}: {e}"
            self.assertEqual(response.status_code, 200)
            resp2 = requests.get(url, timeout=3)

            assert response.content == resp2.content, (
                response.content + b"\n\n" + resp2.content
            )

    def test_run_unparsable_url(self) -> None:
        url = "http://222.164.14.168/img_src"
        try:
            response = requests.get(url, proxies=self.proxies)
        except Exception as e:
            assert False, f'It should not error out, but got {e}'

        self.assertEqual(response.status_code, 200)
        resp2 = requests.get(url)
        assert response.content == resp2.content, (
            response.content + b"\n\n" + resp2.content
        )

    def test_malformed_http_request(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('127.0.0.1', self.port))
            sock.sendall(b'GETHTTP/1.1\r\n')
            resp = sock.recv(8192)
        assert b'HTTP/1.1 400 Bad Request' in resp, f'Got {resp} instead'

    def test_url_does_not_exist(self) -> None:
        url = "http://1.1.1.1.1/test"
        response = requests.get(url, proxies=self.proxies)
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
