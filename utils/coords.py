def neighbours(x, y):
    for xoff in range(-1, 2):
        for yoff in range(-1, 2):
            if (abs(xoff) == 1 and yoff == 0) or (xoff == 0 and abs(yoff) == 1):
                yield x+xoff, y+yoff
