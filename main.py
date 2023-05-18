# MIT license; Copyright (c) 2023 Ondrej Sienczak
from drv import display  # Import drivers to speed up display activation
from app import dispman
from uasyncio import run, gather


async def main():
    dispman.owner = dispman.tasks['hourglass']
    await gather(*[t() for t in dispman.tasks.values()])


run(main())
