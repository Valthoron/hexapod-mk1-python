# Copyright 2020 Serdar Üşenmez
# Distributed under the terms of the GNU General Public License v3.0

def toward(current, target, rate):
    if (current < target):
        current += rate
        if (current > target):
            current = target
    elif (current > target):
        current -= rate
        if (current < target):
            current = target

    return current

def saturate(value, minimum, maximum):
    if (value < minimum):
        return minimum
    elif (value > maximum):
        return maximum
    else:
        return value

def linear(x, x1, y1, x2, y2):
    return y1 + (((x - x1) / (x2 - x1)) * (y2 - y1))

def ramp(x, x1, y1, x2, y2):
    if (y1 < y2):
        return saturate(linear(x, x1, y1, x2, y2), y1, y2)
    else:
        return saturate(linear(x, x1, y1, x2, y2), y2, y1)
