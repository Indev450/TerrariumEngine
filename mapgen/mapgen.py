import multiprocessing as mp

from game.block import Block

from worldfile.worldfile import encode


class Mapgen(mp.Process):
    """Base mapgen class"""

    def __init__(self, mods, output, width, height):
        Block.sort_registered_entries()

        self.mods = mods

        self.ofile = open(output, 'wb')

        self.width = width
        self.height = height

        self.foreground = [[0 for i in range(self.width)] for i in range(self.height)]
        self.midground = [[0 for i in range(self.width)] for i in range(self.height)]
        self.background = [[0 for i in range(self.width)] for i in range(self.height)]
        
        self.status = mp.Value('s', 'Wait...')  # String status of a mapgen
        self.complated = mp.Value('d', 0.0)

    def save(self):
        blocksize = int(Block.registered_count()/256) + 1
        data = encode(
            self.foreground,
            self.midground,
            self.background,
            blocksize)
        self.ofile.write(data)
        self.ofile.close()
    
    def put_foreground(self, x, y, blockid):
        self.foreground[y][x] = blockid

    def put_midground(self, x, y, blockid):
        self.midground[y][x] = blockid

    def put_background(self, x, y, blockid):
        self.background[y][x] = blockid
    
    def get_foreground(self, x, y):
        return self.foreground[y][x]
    
    def get_midground(self, x, y):
        return self.midground[y][x]
    
    def get_background(self, x, y):
        return self.background[y][x]
    
    def set_status(self, string=None, complated=None):

    def run(self):
        pass
