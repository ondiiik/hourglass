# MIT license; Copyright (c) 2023 Ondrej Sienczak
from framebuf import FrameBuffer, MONO_HLSB


class MatrixBuffer:
    '''Frame buffer designed for speed optimized repainting.

    Frame buffer providing 2D array access to frame buffers. It also holds information
    about pixels to be repainted to save some time needed for communication with display
    when there is not that much pixels changed during animation.

    :param width:    Display width
    :param height:   Display height
    '''

    def __init__(self,
                 width: int = 8,
                 height: int = 8):
        self._dim = bytearray((width, height))
        self._diml = bytearray((width - 1, height - 1))
        self._buffs = [bytearray(((width + 7) // 8) * height) for _ in range(4)]
        self._pixels = [FrameBuffer(self._buffs[i], width, height, MONO_HLSB) for i in range(2)]
        self._changed = [FrameBuffer(self._buffs[i], width, height, MONO_HLSB) for i in range(2, 4)]
        self._act = 0

        for buff in self._buffs[2:4]:
            for i in range(len(buff)):
                buff[i] = 255

    def __getitem__(self,
                    key: tuple[int, int]) -> tuple[int, int]:
        '''Get pixel state.

        :param key:    Tuple containing x and y display coordinates.

        :return:       Tuple containing pixel value and pixel change state.
        '''
        act = self._act
        return self._pixels[act].pixel(*key), self._changed[act].pixel(*key)

    def __setitem__(self,
                    key: tuple[int, int],
                    value: int) -> None:
        '''Set pixel value.

        Method sets pixel value and set changed state to 1.

        :param key:    Tuple containing x and y display coordinates.
        '''
        grains = self._pixels[self._act]
        if grains.pixel(*key) != value:
            grains.pixel(*key, value)
            self._changed[self._act].pixel(*key, 1)

    def force_all(self) -> None:
        '''Mark all pixels as changed.
        '''
        b = self._buffs[self._act + 2]
        for i in range(len(b)):
            b[i] = 255

    def blit(self,
             fbuf: FrameBuffer,
             x: int,
             y: int,
             key: int = -1) -> None:
        '''Paint frame buffer over pixels.

        :param fbuf:    Frame buffer to be painted.
        :param x:       X coordinate (origin) of frame buffer.
        :param y:       Y coordinate (origin) of frame buffer.
        :param key:     Color marking transparency
        '''
        act = self._act
        self._pixels[act].blit(fbuf, x, y, key)
        b = self._buffs[act + 2]
        for i in range(len(b)):
            b[i] = 255

    @property
    def buffs(self) -> tuple[bytearray, bytearray]:
        '''Get current active buffers.

        :return:    Tuple containing pixels map and changed state map.
        '''
        act = self._act
        return self._buffs[act], self._buffs[act + 2]

    @property
    def pixels(self) -> FrameBuffer:
        '''Get current active frame buffers.

        Returns pixels values buffer directly. This buffer is not intended for modification,
        but it can be used for slightly faster access to pixels in read mode.

        Just note that writing pixels values here does not guarantee that they will be
        drawn as also suitable change state pixel needs to be set. Therefore rather either use
        indexing for setting the pixel as it sets appropriate change state pixel or
        work with sequence of `make_copy` and `use_copy` which compare changes against original
        graphics and calculates change states appropriately. Or call `force_all` to go around
        optimization and force repainting of all pixels.

        :return:    pixels values frame buffer.
        '''
        return self._pixels[self._act]

    def make_copy(self) -> FrameBuffer:
        '''Make and return copy of inactive frame buffers.

        This method can be used to partially repaint copy of current frame buffer.
        When repaint procedure is completed, then there can be called method
        `use_copy` to flip buffers and let copy to be used by display as current display.
        '''
        act = self._act
        next_buf = (act + 1) % 2
        self._buffs[next_buf][:] = self._buffs[act]
        return self._pixels[next_buf]

    def use_copy(self) -> None:
        '''Use copy made by `make_copy`.

        Calculates change states and use modified copy of current buffer.
        '''
        act = self._act
        next_buf = (act + 1) % 2
        chb = self._buffs[next_buf + 2]
        for i, n, o in zip(range(len(chb)), self._buffs[next_buf], self._buffs[act]):
            chb[i] = n ^ o
        self._act = next_buf

    def reset(self,
              fill: bool) -> None:
        '''Reset display to be either fully clear or fully filled.

        :param fill:    Either fill when ``True`` or clear when ``False``.
        '''
        if fill:
            fill = 255

        self.force_all()

        b = self.buffs[0]
        for i in range(len(b)):
            b[i] = fill

