# MIT license; Copyright (c) 2023 Ondrej Sienczak
from machine import Pin


class NSsPin:
    def __init__(self,
                 pin: int):
        self._m = Pin(pin, mode=Pin.OUT, value=1)

    def __enter__(self):
        self._m.value(0)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._m.value(1)


class SsPin:
    def __init__(self,
                 pin: int):
        self._m = Pin(pin, mode=Pin.OUT, value=0)

    def __enter__(self):
        self._m.value(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._m.value(0)
