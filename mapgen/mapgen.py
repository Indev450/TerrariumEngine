import os
import array

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

        self.worldarr = array.array('I')
        self.worldarr.frombytes(bytes(width*height*3*self.worldarr.itemsize))
        
        self.status = status_v  # String status of a mapgen
        self.done = done_v  # How much work done (in percent)
    
    def is_position_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def save(self):
        data = encode(
                self.worldarr,
                self.width, self.height)
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
            self._set_block_id(x, y, 0, blockid)

    def put_midground(self, x, y, blockid):
        if self.is_position_valid(x, y):
            self._set_block_id(x, y, 1, blockid)

    def put_background(self, x, y, blockid):
        if self.is_position_valid(x, y):
            self._set_block_id(x, y, 2, blockid)
    
    def get_foreground(self, x, y):
        if self.is_position_valid(x, y):
            return self._get_block_id(x, y, 0)
        
    def get_midground(self, x, y):
        if self.is_position_valid(x, y):
            return self._get_block_id(x, y, 1)
    
    def get_background(self, x, y):
        if self.is_position_valid(x, y):
            return self._get_block_id(x, y, 2)
        
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
    
    def _get_block_index(self, x, y, layer):
        '''Get index for array('I', <world>)'''
        return self.width*y*3 + x*3 + layer
    
    def _get_block_id(self, x, y, layer):
        '''Get block identifier at given position and layer'''
        i = self._get_block_index(x, y, layer)
        
        return self.worldarr[i]
    
    def _set_block_id(self, x, y, layer, id):
        '''Set block identifier at given position and layer'''
        i = self._get_block_index(x, y, layer)
        
        self.worldarr[i] = id
