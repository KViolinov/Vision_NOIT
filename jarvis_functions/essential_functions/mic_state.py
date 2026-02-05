import threading

mic_muted = False
lock = threading.Lock()


def toggle_mic():
    global mic_muted
    with lock:
        mic_muted = not mic_muted
        return mic_muted


def is_muted():
    with lock:
        return mic_muted
