import time


def brenchmark(func):
    def wrapper(*args):
        start = time.time()
        func(*args)
        end = time.time()
        print('[ANALYS] Время ' + str(end - start) + ' ' + func.__name__)
    return wrapper