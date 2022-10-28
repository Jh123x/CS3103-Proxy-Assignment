from .ProxyHandler import AtkProxyHandler, ImgSubProxyHandler, GenericProxyHandler


class ProxyFactory:
    @staticmethod
    def create_proxy(atk_mode: int, img_sub_mode: int):
        if atk_mode == 1:
            return AtkProxyHandler

        if img_sub_mode == 1:
            return ImgSubProxyHandler

        return GenericProxyHandler
