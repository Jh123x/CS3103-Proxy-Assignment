import socket
import requests
import unittest
import multiprocessing as mp

from .constants import CONTROL_URL, TEST_URL, TEST_PORT
from .utils import proxy_stdout_bypass


class TestAtkProxy(unittest.TestCase):
    """Test the default setup of the Proxy"""

    def setUp(self) -> None:
        self.port = TEST_PORT
        self.p = mp.Process(target=proxy_stdout_bypass,
                            args=(self.port, 1, 0))
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
            s.proxies = self.proxies
            response = s.get(CONTROL_URL, proxies=self.proxies)
            self.assertEqual(response.status_code, 200)
            resp2 = requests.get(CONTROL_URL)

            assert response.content != resp2.content, (
                response.content + b"\n\n" + resp2.content
            )
            assert (
                b"<html><div>You are being attacked</div><html>" == response.content
            ), "Attack mode missing line."
            assert response.headers['Content-Type'] == 'text/html', "Wrong Content Type"
            assert int(response.headers['Content-Length']) == len(
                response.content
            ), f"Expected {len(response.content)} but got {response.headers['Content-Length']}"

    def test_run_default_test_cases(self) -> None:
        for url in TEST_URL:
            response = requests.get(url, proxies=self.proxies)
            self.assertEqual(response.status_code, 200)
            resp2 = requests.get(url)

            assert response.content != resp2.content, (
                response.content + b"\n\n" + resp2.content
            )
            assert (
                b"<html><div>You are being attacked</div><html>" == response.content
            ), f"Attack mode missing line, got {response.content} instead."
            assert response.headers['Content-Type'] == 'text/html', "Wrong Content Type"
            assert int(response.headers['Content-Length']) == len(
                response.content
            ), f"Expected {len(response.content)} but got {response.headers['Content-Length']}"

    def test_malformed_http_request(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('127.0.0.1', self.port))
            sock.sendall(b'GETHTTP/1.1\r\n\r\n')
            resp = sock.recv(8192)
        assert b'HTTP/1.1 400 Bad Request' in resp, f'Got {resp} instead'

    def test_url_does_not_exist(self) -> None:
        url = "http://1.1.1.1.1/test"
        response = requests.get(url, proxies=self.proxies)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
