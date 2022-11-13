import socket


class RecvFile:
    def __init__(self: 'RecvFile', soc: socket.socket, buff_size: int = 8192) -> None:
        self.soc = soc
        self.step_size = 1
        self.buff_size = buff_size
        self.headers_raw = b''
        self.headers = {}
        self.length = 0
        self.method_header = b''
        self.content = b''
        try:
            self.recv_headers()
            self.recv_content()
        except Exception as e:
            print('Error while receiving file', e)
            raise

    def recv_headers(self: 'RecvFile') -> None:
        if self.headers_raw:
            return

        while True:
            self.headers_raw += self.soc.recv(self.step_size)
            if b'\r\n\r\n' in self.headers_raw:
                break

        self.method_header, headers = self.headers_raw.split(
            b'\r\n')[0], self.headers_raw.split(b'\r\n')[1:]

        for r in headers:
            if not r:
                continue
            k, v = list(map(lambda x: x.strip().lower(), r.split(b': ')))
            self.headers[k] = v

    def handle_default(self: 'RecvFile', length) -> None:
        while len(self.content) < length:
            self.content += self.soc.recv(self.buff_size)

    def handle_chunked(self: 'RecvFile') -> None:
        content = b''
        while b'\r\n\r\n' not in content:
            content += self.soc.recv(self.buff_size)
        self.content = content

    def handle_error(self: 'RecvFile', error_msg: bytes) -> None:
        self.headers_raw = b'HTTP/1.1 500 Internal Server Error\r\n\r\n'
        self.content = b'Error while receiving file: %s \r\n\r\n' % error_msg

    def recv_content(self: 'RecvFile') -> None:
        if self.content:
            return
        if b'content-length' in self.headers:
            self.length = int(self.headers.get(b'content-length', 0))
            return self.handle_default(self.length)
        return self.handle_chunked()

    def get_headers(self: 'RecvFile') -> dict:
        return self.headers

    def get_raw_headers(self: 'RecvFile') -> bytes:
        return self.headers_raw

    def get_content(self: 'RecvFile') -> bytes:
        return self.content
