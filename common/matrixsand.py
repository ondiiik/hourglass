# SPDX-FileCopyrightText: 2020 Carter Nelson for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#
# Note: Optimized for Micropython by OSi (2023)
from .itertools import product_rnd
from .matrixbuffer import MatrixBuffer
from random import getrandbits


class MatrixSand(MatrixBuffer):
    """Extension of frame buffer with capability of animating the sand."""

    def __init__(self, width: int = 8, height: int = 8):
        super().__init__(width, height)
        self._len = 0

    def __len__(self) -> int:
        """Count of grains."""
        return self._len

    def __setitem__(self, key: tuple[int, int], value: int) -> None:
        """Override item assignment of pixels/grains to display.

        This overrides original pixel assignment to support easy and fast counting
        of grains.
        """
        grains = self._pixels[self._act]
        if grains.pixel(*key) != value:
            self._len += 1 if value else -1
            grains.pixel(*key, value)
            self._changed[self._act].pixel(*key, 1)

    def iterate(self, ax: float, ay: float) -> bool:
        """Iterate sand grains animation.

        Process one sand grains animation step in direction of gravity.

        :param ax:    Accelerometer (gravity) in direction X
        :param ay:    Accelerometer (gravity) in direction Y

        :return:    State if something has been animated or not
        """
        # unit vectors for accelerometer
        ix = iy = 0
        if abs(ax) > 0.01:
            ratio = abs(ay / ax)
            if ratio < 2.414:  # tan(67.5deg)
                ix = 1 if ax > 0 else -1
            if ratio > 0.414:  # tan(22.5deg)
                iy = 1 if ay > 0 else -1
        else:
            iy = 1 if ay > 0 else -1

        # buffer
        grains = self.pixels
        new_grains = self.make_copy()
        animated = False

        # loop through the grains
        for x, y in product_rnd(*self._dim):
            # is there a grain here?
            if grains.pixel(x, y):
                moved = False
                # compute new location
                newx = x + ix
                newy = y + iy
                # bounds check
                newx = max(min(self._diml[0], newx), 0)
                newy = max(min(self._diml[1], newy), 0)
                # wants to move?
                if x != newx or y != newy:
                    moved = animated = True
                    # is it blocked?
                    if new_grains.pixel(newx, newy):
                        # can we move diagonally?
                        if not new_grains.pixel(x, newy) and not new_grains.pixel(
                            newx, y
                        ):
                            # can move either way
                            # move away from random side
                            if getrandbits(1):
                                newy = y
                            else:
                                newx = x
                        elif not new_grains.pixel(x, newy):
                            # move in y only
                            newx = x
                        elif not new_grains.pixel(newx, y):
                            # move in x only
                            newy = y
                        else:
                            # nope, totally blocked
                            moved = animated = False
                # did it move?
                if moved:
                    new_grains.pixel(x, y, 0)
                    new_grains.pixel(newx, newy, 1)

        # Repaint done - flip buffers
        self.use_copy()

        return animated

    def reset(self, fill: bool) -> None:
        """Reset display to be either fully clear or fully filled.

        :param fill:    Either fill when ``True`` or clear when ``False``.
        """
        if fill:
            fill = 255
            self._len = 64
        else:
            self._len = 0

        self.force_all()

        b = self.buffs[0]
        for i in range(len(b)):
            b[i] = fill
