from Proxy import start


def proxy_stdout_bypass(port, atk, img_re, _) -> None:
    return start(port, f"{atk}{img_re}")
