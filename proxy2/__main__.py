import argparse
import socket
import sys
from _thread import start_new_thread


def start(listening_port: int, max_connection: int = 5, buffer_size: int = 8192):  # Main Program
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", listening_port))
        sock.listen(max_connection)
        print("Server started successfully [ %d ]" % (listening_port))
    except Exception as e:
        print("Unable to Initialize Socket")
        print(e)
        sys.exit(2)

    while True:
        try:
            conn, addr = sock.accept()  # Accept connection from client browser
            data = conn.recv(buffer_size)  # Recieve client data
            start_new_thread(conn_string, (conn, data, addr, buffer_size)
                             )  # Starting a thread
        except KeyboardInterrupt:
            sock.close()
            print("\n[*] Graceful Shutdown")
            sys.exit(1)


def conn_string(conn, data, addr, buffer_size=8192):
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
        proxy_server(webserver, port, conn, addr, data, buffer_size)
    except Exception:
        pass


def proxy_server(webserver, port, conn, addr, data, buffer_size=8192):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((webserver, port))
        sock.send(data)
        while 1:
            reply = sock.recv(buffer_size)
            if len(reply) > 0:
                conn.send(reply)
                conn.send("\r\n")

                dar = float(len(reply))
                dar = float(dar / 1024)
                dar = "%.3s" % (str(dar))
                dar = "%s KB" % (dar)
                print("%s, %s" % (str(addr[0]), str(dar)))

            else:
                break

    except socket.error as err:
        print(err)
    finally:
        sock.close()
        conn.close()
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Proxy", description="A CS3103 Proxy", epilog="Enjoy the program! :)"
    )
    parser.add_argument(
        "port",
        metavar="port",
        type=int,
        help="Port number: The port to run the proxy on.",
    )
    parser.add_argument(
        "image_sub_mode",
        nargs="?",
        type=int,
        help="Image substitution mode: 1 to activate, others to deactivate.",
        default=0,
    )
    parser.add_argument(
        "attacker_mode",
        nargs="?",
        type=int,
        help="Attacker Mode: 1 to activate, others to deactivate.",
        default=0,
    )
    args = parser.parse_args()

    port = args.port
    image_replacement = args.image_sub_mode
    attack = args.attacker_mode

    start()
