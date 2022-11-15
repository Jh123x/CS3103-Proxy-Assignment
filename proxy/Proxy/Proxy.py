from _thread import start_new_thread
import re
import socket
from urllib.parse import urlparse


from .Helper.RecvFile import RecvFile
from .constants import ALT_IMG_SERVER, ALT_IMG_PORT, ALT_IMAGE_LOC

cache = {}


def generic_mode(
    conn: socket.socket,
    webserver: bytes,
    port: int,
    data_recv: bytes,
    buffer_size: int = 8192,
    url: bytes = b"",
) -> None:
    key = (webserver, port, data_recv)
    if key in cache:
        send_data = cache[key]
        content_len = len(send_data)
        conn.send(send_data)
        conn.close()
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    content_len = 0
    try:

        sock.connect((webserver, port))
        sock.send(data_recv)
        recv_file = RecvFile(sock, buffer_size)
        whole_content = recv_file.get_raw_headers() + recv_file.get_content()
        content_len = len(whole_content)
        conn.send(whole_content)
        cache[key] = whole_content
    except socket.timeout as err:
        conn.send(b"HTTP/1.1 408 Request Timeout\r\n\r\n")
    except socket.error as err:
        print(err)
    except Exception as err:
        print(err)
    finally:
        sock.close()
        conn.close()
        print(f"{url.decode()}, {content_len}")


def atk_mode(
    conn: socket.socket,
    *_,
) -> None:
    url: bytes = _[-1]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data = b"HTTP/1.1 200 OK\r\n\r\nYou are being attacked"
    try:
        conn.send(data)
        print(f"{url.decode()}, {len(data)}")
    except socket.error as err:
        print(err)
    finally:
        sock.close()
        conn.close()


def pic_mode(
    conn: socket.socket,
    webserver: bytes,
    port: int,
    data_recv: bytes,
    buffer_size: int = 8192,
    url: bytes = b"",
):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((webserver, port))
        sock.send(data_recv)
        recv_file = RecvFile(sock, buffer_size)
        content_type = recv_file.get_headers().get(b"content-type", b"")
        if content_type.startswith(b"image"):
            webserver = ALT_IMG_SERVER
            port = ALT_IMG_PORT
            tmp = data_recv.split(b"\r\n")
            tmp[0] = b"GET " + ALT_IMAGE_LOC + b" HTTP/1.1"
            data_recv = b"\r\n".join(tmp)
        generic_mode(conn, webserver, port, data_recv, buffer_size, url)
    except socket.error as err:
        print(err)
    finally:
        sock.close()
        conn.close()


d = {"10": atk_mode, "11": atk_mode, "01": pic_mode, "00": generic_mode}
regex = re.compile(r"^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?")


def setup_connection(
    conn: socket.socket, data: bytes, mode: str, buffer_size: int = 8192
) -> None:
    url = data.split(b"\r\n")[0].split(b" ")[1]
    parsed_url = urlparse(url)
    webserver = parsed_url.hostname or url
    port = parsed_url.port or 80
    print(data)
    return d.get(mode, generic_mode)(conn, webserver, port, data, buffer_size, url)


def start(
    listening_port: int, mode: str, max_connection: int = 5, buffer_size: int = 8192
):  # Main Program
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("", listening_port))
        sock.listen(max_connection)
        print(f"Server started successfully on {listening_port}")
    except Exception as e:
        print(f"Unable to Initialize Socket: {e}")

    while True:
        try:
            conn, _ = sock.accept()  # Accept connection from client browser
            data = conn.recv(buffer_size)  # Receive client data
            start_new_thread(
                setup_connection, (conn, data, mode, buffer_size)
            )  # Starting a thread
        except KeyboardInterrupt:
            sock.close()
            print("\nShutting down")
