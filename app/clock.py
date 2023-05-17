from .task import Task
from common.matrixbuffer import MatrixBuffer
from common.glyphs import glyphs_clock
from common.atools import core_task
from machine import RTC
from uasyncio import sleep_ms, create_task
from utime import ticks_ms
from config import WIFI, NTP_SERVER, TIME_ZONE_HOURS, CLOCK_BRIGHT_TIME, BRIGHTNESS
import network
import ntptime


class Clock(Task):
    def __init__(self):
        super().__init__('clock')
        self.display = MatrixBuffer(), MatrixBuffer()
        self.rtc = RTC()
        self.last = -1, -1
        self.shift = 0
        self.now = ticks_ms()
        self.dispman = None

    @core_task
    async def __call__(self):
        create_task(self._gestures())
        create_task(self._sync())

        self.dispman = self.tasks['dispman']
        self.dispman.brightness(self, 0)

        # Precision of RTC on ESP8266 is horrible.
        # Rather use sys-tick for measuring and
        # RTC for synchronization only.
        while True:
            self._update_time()
            self._draw_time()
            self.dispman.keep_alive(self)
            await sleep_ms(1000)

    def redraw(self):
        self.last = -1, -1

    @core_task
    async def _sync(self):
        while True:
            # NTP sync once every 24 hours
            create_task(self._ntp())
            await sleep_ms(86400000)

    async def _ntp(self):
        # Try to synchronize clocks from internet
        print('Activating NIC')
        nic = network.WLAN(network.STA_IF)
        nic.active(True)
        print('Scanning WiFi')
        channels = nic.scan()
        for wifi_user in WIFI:
            if [True for channel in channels if wifi_user[0] == channel[0]]:
                break
        else:
            wifi_user = None

        if wifi_user is None:
            # No internet - no precise time
            print('No WiFi found')
            return

        # Connect to WiFi
        print('Connecting to', wifi_user[0].decode())
        nic.connect(*wifi_user)

        for retry in range(100):
            if nic.isconnected():
                break
            self._draw_time()
            self.dispman.brightness(self, 5 * (retry % 2))
            await sleep_ms(100)

        if retry == 99:
            print('Not-Connected')
            return

        self.dispman.brightness(self, 0)
        print('Synchronizing time with', NTP_SERVER)
        ntptime.host = NTP_SERVER
        ntptime.settime()

        print('Disconnected')
        if nic.isconnected():
            nic.disconnect()
        nic.active(False)

        now = self.rtc.datetime()
        self.shift = ticks_ms() - now[4] * 3600000 - now[5] * 60000 - now[6] * 1000 - now[7] - TIME_ZONE_HOURS * 3600000

    def _update_time(self):
        self.now = ticks_ms() - self.shift
        while self.now > 86400000:
            self.shift += 86400000
            self.now -= 86400000

    def _draw_time(self):
        h, m = divmod(self.now, 3600000)
        m //= 60000
        now = h, m

        if self.last != now:
            self.last = now

            self.display[0].blit(glyphs_clock[h % 10], 0, 0)
            if h > 9:
                self.display[0].blit(glyphs_clock[h // 10 * 10], 0, 0, 0)

            self.display[1].blit(glyphs_clock[m % 10], 0, 0)
            if m > 9:
                self.display[1].blit(glyphs_clock[m // 10 * 10], 0, 0, 0)
            else:
                self.display[1].blit(glyphs_clock[100], 0, 0, 0)

            self.dispman.draw(self)
            self.dispman.brightness(self, BRIGHTNESS if h in range(*CLOCK_BRIGHT_TIME) else 0)

    @core_task
    async def _gestures(self):
        dispman = self.tasks['dispman']
        async for _ in self.tasks['gestures'].register(self, '*'):
            dispman.owner = self.tasks['hourglass']
