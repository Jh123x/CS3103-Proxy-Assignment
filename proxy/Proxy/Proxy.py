from _thread import start_new_thread
import re
import socket
from urllib.parse import urlparse

from .Helper.RecvFile import RecvFile
from .constants import ALT_IMG_SERVER, ALT_IMG_PORT, ALT_IMAGE_LOC


def generic_mode(
    conn: socket.socket,
    webserver: bytes,
    port: int,
    data_recv: bytes,
    buffer_size: int = 8192,
    url: bytes = b"",
) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    content_len = 0
    try:
        sock.connect((webserver, port))
        sock.settimeout(None)
        sock.send(data_recv)
        recv_file = RecvFile(sock, buffer_size)
        data = recv_file.get_raw_headers() + recv_file.get_content()
        content_len = len(recv_file.get_content())
    except socket.timeout:
        data = b"HTTP/1.1 408 Request Timeout\r\n\r\n"
    except Exception as e:
        data = b"HTTP/1.1 400 Bad Request\r\n\r\n"
    finally:
        conn.send(data)
        conn.close()
        sock.close()
        print(f"{url.decode()}, {content_len}")


def atk_mode(
    conn: socket.socket,
    *_,
) -> None:
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: Close\r\nContent-Length: 45\r\n\r\n<html><div>You are being attacked</div><html>\r\n\r\n"
    try:
        url: bytes = _[-1]
        print(f"{url.decode()}, 45")
    except:
        data = b"HTTP/1.1 400 Bad Request\r\n\r\n"
    finally:
        conn.send(data)
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
    except Exception as e:
        data = b"HTTP/1.1 400 Bad Request\r\n\r\n" + \
            b"Error: " + f"{e}".encode() + b"\r\n\r\n"
        conn.send(data)
        print(f"{url.decode()}, {len(data)}")
    finally:
        sock.close()
        conn.close()


d = {"10": atk_mode, "11": atk_mode, "01": pic_mode, "00": generic_mode}
regex = re.compile(
    r"^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?")


def setup_connection(
    conn: socket.socket, data: bytes, mode: str, buffer_size: int = 8192
) -> None:
    try:
        url = data.split(b"\r\n")[0].split(b" ")[1]
        parsed_url = urlparse(url)
        webserver = parsed_url.hostname or url
        port = parsed_url.port or 80
        return d.get(mode, generic_mode)(conn, webserver, port, data, buffer_size, url)
    except IndexError:
        conn.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
    except Exception:
        conn.send(b"HTTP/1.1 400 Bad Request\r\n\r\n")
    finally:
        conn.close()


def start(
    listening_port: int, mode: str, max_connection: int = 5, buffer_size: int = 8192
) -> None:  # Main Program
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("", listening_port))
        sock.listen(max_connection)
        print(f"Server started successfully on {listening_port}")
    except Exception as e:
        print(f"Unable to Initialize Socket: {e}")

    try:
        while True:    
            conn, _ = sock.accept()  # Accept connection from client browser
            data = conn.recv(buffer_size)  # Receive client data
            start_new_thread(
                setup_connection, (conn, data, mode, buffer_size)
            )  # Starting a thread
    except KeyboardInterrupt:
        print("\nShutting down")
    except Exception as e:
        print('\nServer failed to start: ',e )
    finally:
        sock.close()
