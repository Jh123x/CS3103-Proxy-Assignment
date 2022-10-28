from http.server import BaseHTTPRequestHandler

class ImgSubProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Image substitution mode"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Image substitution mode")