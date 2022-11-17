from Proxy import start


def proxy_stdout_bypass(port, atk, img_re) -> None:
    mode = f"{atk}{img_re}"
    print(f"Starting in: {mode}")
    return start(port, mode)
