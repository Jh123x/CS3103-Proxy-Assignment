from http.server import BaseHTTPRequestHandler


class AtkProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Attack mode"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"You are being attacked")