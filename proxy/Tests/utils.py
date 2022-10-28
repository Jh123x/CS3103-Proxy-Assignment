import os
from Proxy import run_proxy

def proxy_stdout_bypass(port, atk, img_re, w) -> None:
    return run_proxy(port, atk, img_re)