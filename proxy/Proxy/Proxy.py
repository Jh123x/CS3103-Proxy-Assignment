import multiprocessing as mp
from http.server import ThreadingHTTPServer
from .ProxyFactory import ProxyFactory


class Proxy:
    cache = {}

    def __init__(
        self: "Proxy", port: int, atk: int, img_sub: int, ip: str = "localhost"
    ) -> None:
        self.server = ThreadingHTTPServer(
            (ip, port), ProxyFactory.create_proxy(atk, img_sub)
        )

    def serve_forever(self: "Proxy") -> None:
        self.server.serve_forever()
