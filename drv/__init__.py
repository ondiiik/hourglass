# MIT license; Copyright (c) 2023 Ondrej Sienczak
from machine import Pin, SPI, I2C
from config import PIN_SDA, PIN_SCL, SPI_ID, PIN_BEEPER

from .max7219 import Matrix8x8  # Initialize display as early as possible
from .beeper import Beeper

spi = SPI(SPI_ID, baudrate=10000000)
display = Matrix8x8(spi, 15, 2)

from .adxl345 import Adxl345  # Continue by importing of accelerometer

i2c = I2C(scl=Pin(PIN_SCL), sda=Pin(PIN_SDA), freq=400000)
accel = Adxl345(i2c)
beeper = Beeper(PIN_BEEPER)