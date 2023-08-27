# MIT license; Copyright (c) 2023 Ondrej Sienczak
from collections import deque
from uasyncio import Event
from machine import reset
from usys import print_exception


def core_task(coro):
    async def wrapper(*args, **kw):
        nonlocal coro
        try:
            await coro(*args, **kw)
        except Exception as e:
            print_exception(e)
        else:
            print(f"Task {coro} exited !!!")
        reset()

    return wrapper


class azip:
    def __init__(self, *iterators):
        self.iterators = [
            i.__aiter__() if hasattr(i, "__aiter__") else iter(i) for i in iterators
        ]

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            ret = []
            for i in self.iterators:
                ret.append(await i.__anext__() if hasattr(i, "__anext__") else next(i))
            return ret
        except StopIteration as e:
            raise StopAsyncIteration(str(e))


class Queue:
    def __init__(self, maxlen: int):
        self._q = deque(tuple(), maxlen)
        self._e = Event()

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.recv()

    def send(self, value):
        self._q.append(value)
        self._e.set()

    async def recv(self):
        if len(self._q) == 0:
            self._e.clear()
            await self._e.wait()
        return self._q.popleft()
