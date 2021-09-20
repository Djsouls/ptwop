import threading


DEBUG = True


def debug(msg):
    if DEBUG:
        print(f'<{threading.currentThread().getName()}> -- {msg}')


def client_debug(msg):
    if DEBUG:
        print(f'<{threading.currentThread().getName()}> -- [CLIENT]: {msg}')


def server_debug(msg):
    if DEBUG:
        print(f'<{threading.currentThread().getName()}> -- [SERVER]: {msg}')
