import socket
from _thread import start_new_thread
from .Helper.RecvFile import RecvFile
from .constants import ALT_IMG_SERVER, ALT_IMG_PORT, ALT_IMAGE_LOC

cache = {}


def generic_mode(
    conn: socket.socket,
    webserver: bytes,
    port: int,
    data_recv: bytes,
    buffer_size: int = 8192,
) -> None:
    key = (webserver, port, data_recv)
    if key in cache:
        send_data = cache[key]
        content_len = len(send_data)
        conn.send(send_data)
        conn.close()
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        print(err.with_traceback())
    finally:
        sock.close()
        conn.close()
        print(f"{webserver.decode()}, {content_len}")


def atk_mode(
        conn: socket.socket,
        *_,
) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        conn.send(b"HTTP/1.1 200 OK\r\n\r\nYou are being attacked")
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
):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((webserver, port))
        sock.send(data_recv)
        recv_file = RecvFile(sock, buffer_size)
        content_type = recv_file.get_headers().get(b'content-type', '')
        if content_type.startswith(b'image'):
            webserver = ALT_IMG_SERVER
            port = ALT_IMG_PORT
            tmp = data_recv.split(b'\r\n')
            tmp[0] = b'GET ' + ALT_IMAGE_LOC + b' HTTP/1.1'
            data_recv = b'\r\n'.join(tmp)
        generic_mode(conn, webserver, port, data_recv, buffer_size)
    except socket.error as err:
        print(err)
    finally:
        sock.close()
        conn.close()


d = {
    '10': atk_mode,
    '11': atk_mode,
    '01': pic_mode,
    '00': generic_mode
}


def conn_string(conn, data, mode, buffer_size=8192):
    try:
        first_line = data.split(b"\n")[0]
        url = first_line.split()[1]
        http_pos = url.find(b"://")  # Finding the position of ://
        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos + 3):]

        port_pos = temp.find(b":")

        webserver_pos = temp.find(b"/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        if port_pos == -1 or webserver_pos < port_pos:
            port = 80
            webserver = temp[:webserver_pos]
        else:
            port = int((temp[(port_pos + 1):])[: webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]
        d.get(mode)(conn, webserver, port, data, buffer_size)
    except Exception:
        pass


def start(listening_port: int, mode: str, max_connection: int = 5, buffer_size: int = 8192):  # Main Program
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", listening_port))
        sock.listen(max_connection)
        print(f"Server started successfully on {listening_port}")
    except Exception as e:
        print(f"Unable to Initialize Socket: {e}")

    while True:
        try:
            conn, addr = sock.accept()  # Accept connection from client browser
            data = conn.recv(buffer_size)  # Receive client data
            start_new_thread(
                conn_string,
                (conn, data, mode, buffer_size)
            )  # Starting a thread
        except KeyboardInterrupt:
            sock.close()
            print("\nShutting down")
