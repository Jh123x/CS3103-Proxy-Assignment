import argparse
from Proxy import start


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

    start(
        port,
        f"{attack}{image_replacement}"
    )
