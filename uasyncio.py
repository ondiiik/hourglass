# Emulation

from asyncio import *

async def sleep_ms(ms):
    await sleep(ms/1000)
