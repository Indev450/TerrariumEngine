import os

import multiprocessing as mp

from game.block import Block

from worldfile.worldfile import encode

from mods.manager import getmanager


class Mapgen(mp.Process):
    """Base mapgen class"""

    def __init__(self, mods, output, width, height, status_v, done_v):
        super().__init__()

        Block.sort_registered_entries()
        
        self.mods = mods

        self.ofile = open(os.path.join(output, 'world.tworld'), 'wb')

        self.width = width
        self.height = height

        self.foreground = [[0 for i in range(self.width)] for i in range(self.height)]
        self.midground = [[0 for i in range(self.width)] for i in range(self.height)]
        self.background = [[0 for i in range(self.width)] for i in range(self.height)]
        
        self.status = status_v  # String status of a mapgen
        self.done = done_v  # How much work done (in percent)
    
    def is_position_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def save(self):
        blocksize = int(Block.registered_count()/256) + 1
        data = encode(
            self.foreground,
            self.midground,
            self.background,
            blocksize)
        self.ofile.write(data)
        self.ofile.close()
        
        self.set_status(done=-1)
    
    def put_blocks(self, x, y, blocks):
        self.put_foreground(x, y, blocks[0])
        self.put_midground(x, y, blocks[1])
        self.put_background(x, y, blocks[2])
    
    def get_blocks(self, x, y):
        return (
            self.get_foreground(x, y),
            self.get_midground(x, y),
            self.get_background(x, y),
        )
    
    def put_foreground(self, x, y, blockid):
        if self.is_position_valid(x, y):
            self.foreground[y][x] = blockid

    def put_midground(self, x, y, blockid):
        if self.is_position_valid(x, y):
            self.midground[y][x] = blockid

    def put_background(self, x, y, blockid):
        if self.is_position_valid(x, y):
            self.background[y][x] = blockid
    
    def get_foreground(self, x, y):
        if self.is_position_valid(x, y):
            return self.foreground[y][x]
        
    def get_midground(self, x, y):
        if self.is_position_valid(x, y):
            return self.midground[y][x]
    
    def get_background(self, x, y):
        if self.is_position_valid(x, y):
            return self.background[y][x]
        
    def set_status(self, string=None, done=None):
        if string is not None:
            with self.status.get_lock():
                self.status.value = string
        
        if done is not None:
            with self.done.get_lock():
                self.done.value = done

    def run(self):
        self.set_status(string="Initializing mods...", done=0)
        
        manager = getmanager()
        
        manager.call_handlers('init_mapgen', self)
