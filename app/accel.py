from .task import Task
from drv import accel as accel_drv
from uasyncio import sleep_ms, Event
from config import ACC_COMPENSATE, ACC_TRANSFORM
from common.atools import core_task


class AccelSync:
    def __init__(self, accel):
        self.event = Event()
        self.accel = accel

    def __aiter__(self):
        return self

    async def __anext__(self):
        await self.event.wait()
        self.event.clear()
        return self.accel.gravity


class Accel(Task):
    def __init__(self):
        super().__init__('accel')
        self.gravity = b'\0\0\0'
        self.grav45 = b'\0\0'
        self.listeners = list()
        self.transform = bytes([abs(i)-1 for i in ACC_TRANSFORM]), tuple([1 if i>0 else -1 for i in ACC_TRANSFORM])
        accel_drv.compensate(*ACC_COMPENSATE)

    @core_task
    async def __call__(self):
        t, s = self.transform
        while True:
            g = accel_drv.acc()
            g = [g[t[i]] * s[i] for i in range(3)]
            self.gravity = g
            self.grav45 = -g[2] - g[0], -g[0] + g[2]

            for event in self.listeners:
                event.event.set()

            await sleep_ms(100)

    def register(self):
        event = AccelSync(self)
        self.listeners.append(event)
        return event
