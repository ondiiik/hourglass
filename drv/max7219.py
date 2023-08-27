# MIT license; Copyright (c) 2023 Ondrej Sienczak
from .pin import NSsPin
from micropython import const
from machine import SPI


_DIGIT0 = const(1)
_DECODEMODE = const(9)
_INTENSITY = const(10)
_SCANLIMIT = const(11)
_SHUTDOWN = const(12)
_DISPLAYTEST = const(15)


class Matrix8x8:
    def __init__(self, spi: SPI, cs: int, cnt: int = 1):
        self._cs = NSsPin(cs)
        self._active = True
        self._spi = spi
        self._cmd = bytearray(2)
        self._cnt = cnt
        self._bright = -1

        # Initialize display
        for reg, data in (
            (_SHUTDOWN, 0),
            (_DISPLAYTEST, 0),
            (_SCANLIMIT, 7),
            (_DECODEMODE, 0),
            (_SHUTDOWN, 1),
        ):
            self._write(reg, data)

        # Set minimal brightness
        self.brightness = 0

        # Clean up displays
        self._cmd[1] = 255
        self._cmd[0] = _DIGIT0
        with self._cs:
            for i in range(self._cnt):
                self._spi.write(self._cmd)

        self._cmd[1] = 129
        for row in range(1, 7):
            self._cmd[0] = _DIGIT0 + row
            with self._cs:
                for i in range(self._cnt):
                    self._spi.write(self._cmd)

        self._cmd[1] = 255
        self._cmd[0] = _DIGIT0 + 7
        with self._cs:
            for i in range(self._cnt):
                self._spi.write(self._cmd)

    @property
    def brightness(self) -> int:
        return self._bright

    @brightness.setter
    def brightness(self, value: int) -> None:
        if self._bright != value:
            self._bright = max(0, min(15, value))
            self._write(_INTENSITY, self._bright)

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        value = bool(value)
        if value != self._active:
            self._active = value
            self._write(_SHUTDOWN, 1 if value else 0)

    def show(self, *args: "MatrixBuffer") -> None:
        if not self._active:
            return

        def choose_odd(n: int) -> bool:
            return n[0] % 2

        for row in range(8):

            def choose_row(n: tuple[int, list[int, ...]]) -> int:
                return n[1].buffs[1][row]

            self._cmd[0] = _DIGIT0 + row
            mask = sum(map(choose_row, filter(choose_odd, enumerate(args))))

            with self._cs:
                for i in range(self._cnt):
                    pixels = args[i].buffs[0]

                    if True or mask:
                        self._cmd[1] = pixels[row]
                        self._spi.write(self._cmd)

    def _write(self, reg: int, value: int) -> None:
        self._cmd[0] = reg
        self._cmd[1] = value

        with self._cs:
            for _ in range(self._cnt):
                self._spi.write(self._cmd)
