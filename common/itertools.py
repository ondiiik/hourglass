# MIT license; Copyright (c) 2023 Ondrej Sienczak
from random import getrandbits


def range_rnd(cnt: int):
    return range(cnt) if getrandbits(1) else reversed(range(cnt))


def product_rnd(x_max: int, y_max: int):
    if getrandbits(1):
        for x in range_rnd(x_max):
            for y in range_rnd(y_max):
                yield x, y
    else:
        for y in range_rnd(y_max):
            for x in range_rnd(x_max):
                yield x, y
