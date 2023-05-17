from .task import Task
from common.matrixbuffer import MatrixBuffer
from common.glyphs import glyphs_setup
from uasyncio import sleep_ms, create_task


class Setup(Task):
    def __init__(self):
        super().__init__('setup')
        self.display = MatrixBuffer(), MatrixBuffer()
        self.anim_delay = 10
        self.last = 30, 's'
        self.brightness = 2

    async def setup(self):
        hourglass = self.tasks['hourglass']
        dispman = self.tasks['dispman']
        values = 10, 20, 30, 40, 50, \
                 60, 120, 180, 240, 300, 360, 420, 480, 540, \
                 600, 900, 1200, 1500, 1800, 2100, 2400, 2700, 3000, 3300, 3600

        await self._draw(dispman, hourglass)

        async for g in self.tasks['gestures'].register(self, 'UDXE'):
            dispman.keep_alive(self)

            if g == 'X':
                dispman.owner = self.tasks['hourglass']
                break

            if g == 'E':
                l = len(hourglass.display[0])
                if l != 0 and l != 64:
                    create_task(self._clock_reset(dispman, hourglass))
                continue

            final_time = round(hourglass.final_time)

            if g == 'U':
                i = min(len(values) - 1, values.index(final_time) + 1)
                r = True
            elif g == 'D':
                i = max(0, values.index(final_time) - 1)
                r = False

            hourglass.final_time = values[i]
            await self._draw(dispman, hourglass, r)

    async def _draw(self, dispman, hourglass, reverse=True):
        final_time = round(hourglass.final_time)
        vn, sn = (final_time, 's') if final_time < 60 else (final_time // 60, 'm')
        vo, so = self.last
        self.last = vn, sn
        display = self.display
        dispman.brightness(self, self.brightness)

        if vn != vo or sn != so:
            r = range(8)
            if reverse:
                r = reversed(r)
                vo, vn = vn, vo
                so, sn = sn, so

            for i in r:
                if vn != vo:
                    display[0].blit(glyphs_setup[vo], i, -i)
                    display[0].blit(glyphs_setup[vn], i - 7, -i + 7)

                if sn != so:
                    display[1].blit(glyphs_setup[so], i, -i)
                    display[1].blit(glyphs_setup[sn], i - 7, -i + 7)

                dispman.draw(self)

                await sleep_ms(self.anim_delay)
        else:
            # No change - no animation - just draw current state
            display[0].blit(glyphs_setup[vn], 0, 0)
            display[1].blit(glyphs_setup[sn], 0, 0)
            dispman.draw(self)

    async def _clock_reset(self, dispman, hourglass):
        hourglass.reset()
        dispman = self.tasks['dispman']

        for _ in range(2):
            for i in range(16):
                dispman.brightness(self, i)
                await sleep_ms(20 - i)

            sleep_ms(100)

            for i in reversed(range(16)):
                dispman.brightness(self, i)
                await sleep_ms(20 - i)

        for i in range(self.brightness + 1):
            dispman.brightness(self, i)
            await sleep_ms(20 - i)
