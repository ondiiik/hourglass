from uasyncio import sleep_ms
from machine import Pin

class Beeper:
    def __init__(self, pin):
        if pin < 0:
            self._p = None
        else:
            self._p = Pin(pin, Pin.OUT)
            self._p.off()

    async def beep(self, t=100, p=0, c=1):
        if self._p is None:
            await sleep_ms((t + p) * c)
        else:
            try:
                for _ in range(c):
                    self._p.on()
                    await sleep_ms(t)
                    if p:
                        self._p.off()
                        await sleep_ms(p)
            finally:
                self._p.off()
