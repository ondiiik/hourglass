from machine import Pin, SPI, I2C
from .max7219 import Matrix8x8  # Initialize display as early as possible
spi = SPI(1, baudrate=10000000)
display = Matrix8x8(spi, 15, 2)

from .adxl345 import Adxl345  # Continue by importing of accelerometer
i2c = I2C(scl=Pin(4), sda=Pin(5), freq=400000)
accel = Adxl345(i2c)
