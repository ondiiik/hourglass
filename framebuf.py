# Emulation

from __future__ import annotations


from itertools import product


MONO_HLSB = 1


class FrameBuffer:
    def __init__(self, buf: bytearray, width: int, height: int, mode: int):
        self._buf = buf
        self._width = width
        self._rwidth = ((width + 7) // 8) * 8
        self._height = height
        self._mode = mode
        assert mode == MONO_HLSB, "Only MONO_HLSB supported in simulation!"

    def pixel(self, x: int, y: int, val: int = None) -> int:
        if x < 0 or x >= self._width or y < 0 or y >= self._height:
            return 0

        i, r = divmod((y * self._rwidth + x), 8)
        r = 7 - r
        m = 1 << r

        if val is not None:
            if val:
                self._buf[i] |= m
            else:
                self._buf[i] &= ~m
            return val
        else:
            return (self._buf[i] >> r) & 1

    def blit(self, fbuf: FrameBuffer, x: int, y: int, key: int = -1) -> None:
        for yy, xx in product(range(fbuf._width), range(fbuf._height)):
            p = fbuf.pixel(xx, yy)
            if p != key:
                self.pixel(xx + x, yy + y, p)
