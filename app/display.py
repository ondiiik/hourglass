# MIT license; Copyright (c) 2023 Ondrej Sienczak
from .task import Task
from common.matrixbuffer import MatrixBuffer
from common.atools import core_task
from drv import display
from uasyncio import sleep_ms
from random import getrandbits
from config import DIMM_TIME, SAVER_TIME


class DispMan(Task):
    '''Manage display ownership
    '''

    def __init__(self):
        super().__init__('dispman')
        self._owner = None
        self._brights = dict()
        self._saver = 0
        self.display = MatrixBuffer(), MatrixBuffer()

    @core_task
    async def __call__(self):
        while True:
            await sleep_ms(1000)
            self._saver += 1
            
            if self._saver == DIMM_TIME:
                display.brightness = 0
            
            if self._saver == SAVER_TIME:
                await self._screen_saver()

    @property
    def owner(self) -> Task:
        return self._owner

    @owner.setter
    def owner(self,
              owner: Task):
        self._owner = owner
        for d in owner.display:
            d.force_all()
        display.brightness = self._brights.get(owner, 0)

    def draw(self,
             owner: Task) -> None:
        '''Handle display

        Display can be handled by its owner only. Owner is application in foreground.
        or DPMS screen saver.
        '''
        if owner == self._owner and self._saver < SAVER_TIME:
            display.show(*owner.display)

    def brightness(self,
                   owner: Task,
                   value: float) -> None:
        '''Set brightness to be used with next display shot

        :param owner:   Owner requesting to display stuff
        :param value:   Brightness value in range from 0 to 1
        '''
        self._brights[owner] = value
        if owner == self._owner:
            display.brightness = 0 if self._saver > DIMM_TIME else value

    def keep_alive(self,
                   owner: Task = None) -> None:
        '''Reset display keep alive flag
        '''
        if owner is None:
            owner = self._owner

        if owner == self._owner:
            display.brightness = self._brights.get(owner, 0)
            self._saver = 0

    async def _screen_saver(self):
        for d in self.display:
            d.reset(0)

        while self._saver >= SAVER_TIME:
            d = self.display[getrandbits(1)]
            p = getrandbits(3), getrandbits(3)
            d[p] = 1
            await sleep_ms(200+getrandbits(7))
            display.show(*self.display)
            d[p] = 0
