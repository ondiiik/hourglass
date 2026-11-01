# ESP8266 Hourglass

Simple ESP8266 MicroPython based electronic hour glass, useful for some table games
or just to learn small children to get feeling how time flows ;-).

[![hourglass_video](http://img.youtube.com/vi/Gjs1syfmNBQ/0.jpg)](https://youtu.be/Gjs1syfmNBQ)

## Installation

Installation is pretty easy. You just need to flash
[hourglass_esp8266.bin firmware file](https://github.com/ondiiik/hourglass/releases)
into your ESP8266 board.
There is many options how to do it. You can either use
[esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32/) command
(use your USB port instead of `/dev/ttyUSB0`):

```
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 hourglass_esp8266.bin 
```

... or, use of [Thonny IDE](https://thonny.org/) is described here.

If you already do not have [Thonny IDE](https://thonny.org/) installed, you can follow
[this page](https://github.com/thonny/thonny/releases).

1. Run `thonny` and follow menu `Tools -> Options... -> Interpreter`.
2. Choose interpreter `Micropython (ESP8266)`.
3. Click on `Install or update Micropython` in lower right corner.
4. Then select port where your ESP board is connected.
5. Download firmware binary file [hourglass_esp8266.bin](https://github.com/ondiiik/hourglass/releases) from latest releases.
6. Choose downloaded firmware file.
7. Ensure that `Erase flash before installing` check-box is checked to erase actual file system on chip.
   This is needed as this MicroPython image is pre-compiled and set up to create necessary files
   on ESP file system required for startup of Python code automatically.
8. Then click on `Install` and wait till firmware is flashed.

### Setup

After first boot, the default `config.py` file is created. Use Thonny IDE again to modify this file directly
in ESP device.
