# Emulation

import pygame
from common.glyphs import glyphs_clock
from datetime import datetime
from framebuf import FrameBuffer, MONO_HLSB
from itertools import product
from struct import pack
from os import _exit as exit


class RTC:
    def datetime(self):
        #(2023, 5, 6, 5, 9, 23, 20, 146)
        now = datetime.now()
        return now.year, now.month, now.day, now.weekday(), now.hour, now.minute, now.second, now.microsecond // 1000


class Pin:
    def __init__(self,
                 pin: int,
                 mode: int = 2,
                 value: int = 0):
        self._value = value

    def value(self, value: int = None) -> int:
        if value is not None:
            self._value = value
        return self._value

    OUT = 1
    IN = 2


class SPI:
    _dim = 200, 600
    _dsize = round(_dim[0] * 0.7)
    _radius = _dsize / 20
    _step = _dsize / 8
    _step2 = _step / 2
    _buffs = tuple([bytearray(8) for _ in range(3)])

    def __init__(self,
                 idx: int,
                 baudrate: int):
        cls = type(self)

        self._last = -1
        self._intesity = 0

        self._screen = pygame.display.set_mode(self._dim)
        self._clock = pygame.time.Clock()

        cls._pixels = tuple([FrameBuffer(self._buffs[i], 8, 8, MONO_HLSB) for i in range(len(self._buffs))])
        self._pixels[2].blit(glyphs_clock[1], 0, 0)

        self._raw = tuple([bytearray(self._dsize * self._dsize * 3) for i in range(2)])
        self._display = tuple([pygame.image.frombuffer(self._raw[i], (self._dsize, self._dsize), 'RGB') for i in range(2)])

        pygame.display.set_caption('Hourglass simulator')

        self._display_draw()

    def write(self,
              data: bytes) -> None:
        if data[0] in range(1, 9):
            if self._last == data[0]:
                self._buffs[1][data[0] - 1] = data[1]
            else:
                self._buffs[0][data[0] - 1] = data[1]
                self._last = data[0]
        elif data[0] == 10:
            self._intesity = data[1]

        self._display_draw()

    def _display_draw(self):
        clmax = (self._intesity * 10) + 105

        for y, x in product(range(8), range(8)):
            pygame.draw.circle(self._screen, (0, 0, 180 if self._pixels[2].pixel(x, y) else 64), (self._step2 + self._step * x, self._step2 + self._step * y), self._radius)

        for display, pixels in zip(self._display, self._pixels):
            for y, x in product(range(8), range(8)):
                pygame.draw.circle(display, (0, clmax if pixels.pixel(x, y) else 16, 0), (self._step2 + self._step * x, self._step2 + self._step * y), self._radius)

        for i, display in zip(range(2), self._display):
            rotated_image = pygame.transform.rotate(display, 225)
            self._screen.blit(rotated_image, (0, self._dim[1] - self._dim[0] * 2 + i * self._dim[0]))

        pygame.display.flip()
        self._clock.tick(500)


class I2C:
    def __init__(self,
                 scl: Pin,
                 sda: Pin,
                 freq: int):
        self._acc = 0, 0, 1000

    def writeto_mem(self,
                    addr: int,
                    reg: int,
                    data: bytes) -> None:
        ...

    def readfrom_mem_into(self,
                          addr: int,
                          reg: int,
                          buff: bytearray) -> None:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self._acc = 0, 0, -1000
                elif event.key == pygame.K_DOWN:
                    self._acc = 0, 0, 1000
                elif event.key == pygame.K_LEFT:
                    self._acc = 0, -1000, 0
                elif event.key == pygame.K_RIGHT:
                    self._acc = 0, 1000, 0
                elif event.key == pygame.K_q:
                    self._acc = -1000, 0, 0
                elif event.key == pygame.K_a:
                    self._acc = 1000, 0, 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = int(event.pos[0] // SPI._step), int(event.pos[1] // SPI._step)
                SPI._pixels[2].pixel(x, y, not SPI._pixels[2].pixel(x, y))
                print(SPI._buffs[2])

        buff = memoryview(buff)
        buff[:] = pack('<hhh', *self._acc)


def reset():
    print('!!! REBOOT !!!')
    exit(1)
