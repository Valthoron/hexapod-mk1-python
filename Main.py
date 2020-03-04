# Copyright 2020 Serdar Üşenmez
# Distributed under the terms of the GNU General Public License v3.0

import datetime
import numpy
import threading
import time

import Hexapod

def main_loop(period, f):
    def g_tick():
        t = time.time()
        count = 0
        while True:
            count += 1
            yield max(t + (count * period) - time.time(), 0)

    g = g_tick()

    while True:
        time.sleep(next(g))
        f()

try:
    numpy.set_printoptions(suppress=True)
    Hexapod.hexapod_setup()
    main_loop(Hexapod.LOOP_PERIOD, Hexapod.hexapod_main)

except KeyboardInterrupt as e:
    Hexapod.hexapod_shutdown()
    print()
