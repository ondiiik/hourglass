# MIT license; Copyright (c) 2023 Ondrej Sienczak
from .accel import Accel
from .clock import Clock
from .display import DispMan
from .gestures import Gestures
from .hourglass import HourGlass
from .setup import Setup
from gc import collect

gestures = Gestures()
accel = Accel()
hourglass = HourGlass()
dispman = DispMan()
setup = Setup()
clock = Clock()

collect()