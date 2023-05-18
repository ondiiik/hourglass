# MIT license; Copyright (c) 2023 Ondrej Sienczak
from .task import Task
from common import MatrixSand
from common.atools import core_task
from common.vect3d import dominates
from uasyncio import sleep_ms, create_task
from utime import ticks_ms
from gc import collect
from config import CLOCK_TIME, BRIGHTNESS


class HourGlass(Task):
    '''Coroutine task providing hourglass animation
    '''

    def __init__(self):
        super().__init__('hourglass')
        print('Hourglass v1.1 by OSi')
        self.neck_delay = 468.75  # 15.625 * 30 => 30s
        self.anim_delay = 10
        self.pulsing = 0
        self.display = MatrixSand(), MatrixSand()
        self.clock_delay = CLOCK_TIME * 1000

    @property
    def final_time(self) -> float:
        '''Property used to get or set final hourglass time in seconds
        '''
        return self.neck_delay / 15.625

    @final_time.setter
    def final_time(self, value: float) -> None:
        self.neck_delay = value * 15.625

    def reset(self):
        '''Reset hourglass to initial state (sand in top side)
        '''
        self.display[0].reset(True)
        self.display[1].reset(False)

    @core_task
    async def __call__(self):
        '''Main coroutine task handling sand animation
        '''
        neck = (7, 0), (0, 7)

        # Draw initial sand
        self.reset()

        # Activates gestures handling
        create_task(self._gestures())

        # Start animation in main task
        tnext = ticks_ms()
        tclock = tnext + self.clock_delay
        last_len = 0
        accel = self.tasks['accel']
        clock = self.tasks['clock']
        dispman = self.tasks['dispman']
        dispman.brightness(self, BRIGHTNESS)
        while True:
            # Animate gravity
            g_45 = accel.grav45
            for s in self.display:
                if s.iterate(*g_45):
                    dispman.keep_alive(self)

            # Checks if we want launch _pulse
            l = len(s)
            if l != last_len:
                if l == 0 or l == 64:
                    if self.pulsing == 0:
                        create_task(self._pulse())
                    self.pulsing = min(2, self.pulsing + 1)
                last_len = l

            # Process hourglass neck throughput
            g_3d = accel.gravity
            ts = ticks_ms()

            # Only when hourglass are not tilted more than 45 degrees
            d, s = dominates(g_3d)
            if d == 2:
                # Check if there is time for next sand particle
                tclock = ts + self.clock_delay
                if ts > tnext:
                    tnext += self.neck_delay
                    su, sl, nu, nl = (self.display[1], self.display[0], neck[1], neck[0]) \
                        if g_3d[2] > 0 else \
                        (self.display[0], self.display[1], neck[0], neck[1])
                    if su[nu][0] and not sl[nl][0]:
                        su[nu] = 0
                        sl[nl] = 1
            else:
                # No sand is falling - postpone next sand particle for later
                tnext = ts + self.neck_delay
                if d == 0 and s < 0 and dispman.owner is not clock:
                    # When clocks are on right side for a while, show current time
                    if ts > tclock:
                        clock.redraw()
                        dispman.owner = clock
                else:
                    tclock = ts + self.clock_delay

            # Show result and wait next frame
            dispman.draw(self)
            collect()
            await sleep_ms(self.anim_delay)

    @core_task
    async def _gestures(self):
        '''Coroutine task receiving gestures related to hourglass
        '''
        dispman = self.tasks['dispman']
        async for _ in self.tasks['gestures'].register(self, 'E'):
            setup = self.tasks['setup']
            dispman.owner = setup
            create_task(setup.setup())

    async def _pulse(self):
        '''Proceed pulsing of LEDs when clock is over
        '''
        dispman = self.tasks['dispman']
        for _ in range(4):
            for i in range(16):
                dispman.brightness(self, i)
                await sleep_ms(20 - i)

            await sleep_ms(100)

            for i in reversed(range(16)):
                dispman.brightness(self, i)
                await sleep_ms(20 - i)

        for i in range(BRIGHTNESS + 1):
            dispman.brightness(self, i)
            await sleep_ms(20 - i)

        self.pulsing -= 1
        if self.pulsing > 0:
            create_task(self._pulse())
