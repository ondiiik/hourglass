from .task import Task
from common.atools import azip, Queue
from common.vect3d import dominates
from common.atools import core_task
from micropython import const


_G_THR_UP = const(400)
_G_THR_DOWN = const(200)
_DLY_CNT = const(5)
_Q_SIZE = const(3)


class Gestures(Task):
    def __init__(self):
        super().__init__('gestures')
        self._acc = None
        self._listeners = {i: dict() for i in 'EUDLRX*'}
        self._dispman = None
        self._dominating = 0, 0

    @core_task
    async def __call__(self):
        self._acc = self.tasks['accel'].register()
        self._dispman = self.tasks['dispman']

        async for gravity in self._acc:
            d, s = self._dominates(gravity)

            # Any selection sequence starts with display facing up
            if d == 1 and s == 1:
                await self._selection()

    async def _selection(self):
        # Stay checking if we are facing display up
        self._dispman.keep_alive()

        async for gravity in self._acc:
            d, s = self._dominates(gravity)

            # Escape sequence starts with rotating on side
            if d == 0:
                # Check if there is escape sequence pattern or side x pattern
                await self._side_x(s)

                # Wait till returned out from rotated position
                async for gravity in self._acc:
                    d, _ = self._dominates(gravity)
                    if d != 0:
                        break

            # Rotating on top or bottom - side y
            elif d == 2:
                side = s
                self._dispman.keep_alive()
                async for gravity, _ in azip(self._acc, range(_DLY_CNT)):
                    d, s = self._dominates(gravity)

                    # When quickly rotated back then it is gesture
                    if d == 1:
                        self._notify('U' if side > 0 else 'D')
                        break
                else:
                    self._notify('X')
                    return

    async def _side_x(self,
                      side: int) -> None:
        # We was tilted on side. Now check if are rotating from side to display up and back twice
        # in defined interval to activate escape.
        self._dispman.keep_alive()

        for i in b'\x01\0\x01\0\x01':
            async for gravity, _ in azip(self._acc, range(_DLY_CNT)):
                d, s = self._dominates(gravity)

                if d == 2:
                    return
                elif d == i:
                    if i == 1:
                        self._notify('L' if side < 0 else 'R')
                    break
                else:
                    side = s
            else:
                return

        self._notify('E')

    def _notify(self,
                g: str) -> None:
        self._dispman.keep_alive()
        q = self._listeners[g].get(self._dispman.owner, None)
        if q is not None:
            q.send(g)

    def _dominates(self,
                   gravity: tuple) -> tuple:
        d = dominates(gravity)
        if self._dominating != d:
            self._dominating = d
            self._notify('*')
        return d

    def register(self,
                 owner: str,
                 gestures: str) -> None:
        # Register gestures to selected owner
        q = Queue(_Q_SIZE)

        for g in gestures:
            self._listeners[g][owner] = q

        return q
