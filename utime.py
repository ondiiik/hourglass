# Emulation

from time import *

_start = time()

def ticks_ms() -> int:
    return round((time() - _start) * 1000)
