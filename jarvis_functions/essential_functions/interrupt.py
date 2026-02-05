import pygame
import threading

interrupt_flag = False
lock = threading.Lock()


def interrupt():
    global interrupt_flag
    with lock:
        interrupt_flag = True

    # HARD stop audio immediately
    try:
        pygame.mixer.music.stop()
        pygame.mixer.stop()
    except Exception:
        pass


def consume_interrupt():
    """
    Returns True once per interrupt press, then resets.
    """
    global interrupt_flag
    with lock:
        if interrupt_flag:
            interrupt_flag = False
            return True
        return False
