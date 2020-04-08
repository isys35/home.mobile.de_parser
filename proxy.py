from fp.fp import FreeProxy


def get_proxy():
    free_proxy = FreeProxy(rand=True).get()
    proxies = {
     'http': free_proxy.split('/')[-1],
    'https': free_proxy.split('/')[-1]
    }
    return proxies