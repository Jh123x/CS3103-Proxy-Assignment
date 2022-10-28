from Proxy import Proxy

def run_proxy(port: int, attack:int, image_replacement:int) -> None:
    proxy = Proxy(port, attack, image_replacement)
    proxy.serve_forever()