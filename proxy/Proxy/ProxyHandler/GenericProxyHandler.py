from requests import Response, Session
from http.server import BaseHTTPRequestHandler


class CacheItem:
    def __init__(self: "CacheItem", response: Response) -> None:
        self.status_code = response.status_code
        self.headers = response.headers
        self.content = response.content


class GenericProxyHandler(BaseHTTPRequestHandler):
    cache = {}

    def request_url(self: "GenericProxyHandler", url: str) -> CacheItem:
        if url in self.cache:
            return self.cache[url]
        with Session() as s:
            response = s.get(url)
            value = CacheItem(response)
            self.cache[url] = value
            return value

    def do_GET(self) -> None:
        """Default mode"""
        response = self.request_url(self.path)
        self.send_response(response.status_code)

        for k, v in response.headers.items():
            self.send_header(k, v)

        self.end_headers()
        self.wfile.write(response.content)
