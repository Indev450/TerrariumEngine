import random

def randcolor():

    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    return color(r, g, b)


def color(*rgb):

    if len(rgb) == 1:
        rgb = (rgb[0], rgb[0], rgb[0])

    elif len(rgb) != 3:
        raise ValueError(
            f"color() takes 1 or 3 arguments, but {len(rgba)} were given")

    for c in rgb:
        if c not in range(256):
            raise ValueError(f"expected value in range(256), got {c}")

    r, g, b = rgb

    return "#" + _color(r) + _color(g) + _color(b)


def _color(value):

    c = hex(value)[2:]

    if len(c) == 1:
        c = "0" + c

    return c