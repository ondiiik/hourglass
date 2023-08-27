# MIT license; Copyright (c) 2023 Ondrej Sienczak
from .task import Task
from common.matrixbuffer import MatrixBuffer
from common.glyphs import glyphs_clock
from common.atools import core_task
from machine import RTC
from uasyncio import sleep_ms, create_task
from utime import ticks_ms
from config import (
    WIFI,
    NTP_SERVER,
    TIME_ZONE_HOURS,
    CLOCK_BRIGHT_TIME,
    BRIGHTNESS,
    WIFI_TIMEOUT,
    NTP_RETRY,
)
from usys import print_exception
import network
import ntptime


class WiFi:
    def __init__(self, clock: "Clock"):
        self.clock = clock

    async def __aenter__(self):
        if not WIFI:
            print("No WiFi configuration - skiping NTP")
            return

        print("Activating NIC")
        self.nic = network.WLAN(network.STA_IF)
        self.nic.active(True)
        print("Scanning WiFi")
        channels = self.nic.scan()
        for wifi_user in WIFI:
            if [True for channel in channels if wifi_user[0] == channel[0]]:
                break
        else:
            wifi_user = None

        if wifi_user is None:
            # No internet - no precise time
            print("No WiFi found")
            raise RuntimeError("No WiFi found")

        # Connect to WiFi
        print("Connecting to", wifi_user[0].decode())
        self.nic.connect(*wifi_user)

        for retry in range(100):
            if self.nic.isconnected():
                break
            self.clock._draw_time()
            self.clock.dispman.brightness(self, 5 * (retry % 2))
            await sleep_ms(100)

        if retry == WIFI_TIMEOUT * 10:
            print("WiFi not connected")
            raise RuntimeError("WiFi not connected")

        print("WiFi connected")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("Disconnecting ...")
        if self.nic.isconnected():
            self.nic.disconnect()
        self.nic.active(False)
        print("WiFi disconnected")


class Clock(Task):
    def __init__(self):
        super().__init__("clock")
        self.display = MatrixBuffer(), MatrixBuffer()
        self.rtc = RTC()
        self.last = -1, -1
        self.shift = 0
        self.now = ticks_ms()
        self.dispman = None
        self.sync_task = None

    @core_task
    async def __call__(self):
        create_task(self._gestures())
        create_task(self._sync())

        self.dispman = self.tasks["dispman"]
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
        self.sync_task = create_task(self._ntp())
        await sleep_ms(86400000)

        while True:
            # NTP sync once every 24 hours
            if self.sync_task.done():
                self.sync_task = create_task(self._ntp())
            await sleep_ms(86400000)

    async def _ntp(self):
        # Try to synchronize clocks from internet
        while True:
            try:
                async with WiFi(self):
                    for n in range(8):
                        for ntp_server in NTP_SERVER:
                            print("Synchronizing time with", ntp_server)
                            self.dispman.brightness(self, 0)
                            ntptime.host = ntp_server

                            try:
                                ntptime.settime()
                                now = self.rtc.datetime()
                                break
                            except OSError:
                                print("\tNTP timeout - retry", n)
                                await sleep_ms(1000)
                        else:
                            continue

                        self.shift = (
                            ticks_ms()
                            - now[4] * 3600000
                            - now[5] * 60000
                            - now[6] * 1000
                            - now[7]
                            - TIME_ZONE_HOURS * 3600000
                        )
                        print("NTP synchronized")
                        return
            except Exception as e:
                print("NTP sync failed, retry in", NTP_RETRY, "minutes ...")
                print_exception(e)
                await sleep_ms(NTP_RETRY * 60000)

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
            self.dispman.brightness(
                self, BRIGHTNESS if h in range(*CLOCK_BRIGHT_TIME) else 0
            )

    @core_task
    async def _gestures(self):
        dispman = self.tasks["dispman"]
        async for _ in self.tasks["gestures"].register(self, "*"):
            dispman.owner = self.tasks["hourglass"]
