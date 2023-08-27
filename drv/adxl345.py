# MIT license; Copyright (c) 2023 Ondrej Sienczak
from machine import I2C
from struct import unpack
from micropython import const


OFSX = const(0x1E)
OFSY = const(0x1F)
OFSZ = const(0x20)
BW_RATE = const(0x2C)
POWER_CTL = const(0x2D)
INT_ENABLE = const(0x2E)
DATA_FORMAT = const(0x31)
REG_ACC = const(0x32)


class Adxl345:
    def __init__(self, i2c: I2C, addr: int = 0x53):
        self._addr = addr
        self._i2c = i2c
        self._buff = bytearray(6)
        self._regb = bytearray(1)

        self._wrm(DATA_FORMAT, 0x2B)  # Full range
        self._wrm(BW_RATE, 0x0C)  # BW_RATE_50HZ
        self._wrm(INT_ENABLE, 0)  # Disable interrupt
        self._wrm(OFSX, 0)  # Set ACC offsets
        self._wrm(OFSY, 0)
        self._wrm(OFSZ, 0)
        self._wrm(POWER_CTL, 0x28)  # MEASURE continuously

    def acc(self):
        self._i2c.readfrom_mem_into(self._addr, REG_ACC, self._buff)
        return unpack("<hhh", self._buff)

    def compensate(self, x: int, y: int, z: int) -> None:
        self._wrm(OFSX, max(round(x / 8), 0))  # Set ACC offsets
        self._wrm(OFSY, max(round(y / 8), 0))
        self._wrm(OFSZ, max(round(z / 8), 0))

    def _wrm(self, addr: int, value: int) -> None:
        self._regb[0] = value
        self._i2c.writeto_mem(self._addr, addr, self._regb)
