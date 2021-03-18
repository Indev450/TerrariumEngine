import pygame as pg

from utils.coords import neighbours

import game.block as block
from .chunk import Chunk
from .tick import Ticker

from .camera import Camera

from config import getcfg


config = getcfg()


def ids2blocks(blockids, width, height):
    """Make 2d array of Block objects from 2d array of block ids"""
    return [[World.block_by_id(
                blockids[y][x],
                x*block.Block.WIDTH,
                y*block.Block.HEIGHT) for x in range(width)] for y in range(height)]


def blocks2ids(blocks):
    """Make 2d array of block ids from 2d array of Block objects"""
    return [[World.id_from_block(block) for block in line] for line in blocks]



class World:
    instance = None

    CHUNK_WIDTH = config["world.chunk_size"][0]
    CHUNK_HEIGHT = config["world.chunk_size"][1]

    def __init__(self, foreground, midground, background):

        self.set(self)

        print("Initializing blocks...")

        self.WORLD_WIDTH = len(foreground[0])
        self.WORLD_HEIGHT = len(foreground)

        self.foreground = ids2blocks(
            foreground,
            self.WORLD_WIDTH,
            self.WORLD_HEIGHT)

        self.midground = ids2blocks(
            midground,
            self.WORLD_WIDTH,
            self.WORLD_HEIGHT)

        self.background = ids2blocks(
            background,
            self.WORLD_WIDTH,
            self.WORLD_HEIGHT)

        self.chunks_x = self.WORLD_WIDTH//self.CHUNK_WIDTH + 1
        self.chunks_y = self.WORLD_HEIGHT//self.CHUNK_HEIGHT + 1

        self.chunks = [[None for x in range(self.chunks_x)] for y in range(self.chunks_y)]

        self.chunks_loaded = []
        
        self.load_chunk(0, 0)

        self.camera = Camera.get()
        
        self.ticker = Ticker.new()
    
    def get_ticker(self):
        return self.ticker

    def is_collide(self, entity, on_collide):
        # block_w = 16, ent.rect.left = 128, ent.rect.right = 138, range = (8, 9)
        for x in self.worldrange_x(entity.rect.left, entity.rect.right):
            for y in self.worldrange_y(entity.rect.top, entity.rect.bottom):
                if (self.foreground[y][x] is not None and
                    pg.sprite.collide_rect(self.foreground[y][x], entity)):
                    on_collide(self.foreground[y][x])

    def worldrange_x(self, x1, x2):
        return range(max(0, x1//block.Block.WIDTH), min(x2//block.Block.WIDTH + 1, self.WORLD_WIDTH))

    def worldrange_y(self, y1, y2):
        return range(max(0, y1//block.Block.HEIGHT), min(y2//block.Block.HEIGHT + 1, self.WORLD_HEIGHT))

    def draw(self, screen):
        list(
            map(
                lambda chunk: chunk.draw(screen),
                self.chunks_loaded))

    def _setblock_into(self, blocks, x, y, id):
        if not self.within_bounds(x, y):
            return
        
        if blocks[y][x] is not None:
            blocks[y][x].on_destroy()

        blocks[y][x] = self.block_by_id(id,
            x*block.Block.WIDTH,
            y*block.Block.HEIGHT)
        
        if blocks[y][x] is not None:
            blocks[y][x].on_place(x, y)
        
        updated_chunks = []
        
        for cx, cy in neighbours(x, y):
            chunk_x, chunk_y = self.chunk_pos(cx*block.Block.WIDTH, cy*block.Block.HEIGHT)

            if (self.chunks[chunk_y][chunk_x] is not None
               and not self.chunks[chunk_y][chunk_x] in updated_chunks):
                self.chunks[chunk_y][chunk_x].update()
                updated_chunks.append(self.chunks[chunk_y][chunk_x])
            else:
                if not self.chunks[chunk_y][chunk_x] in updated_chunks:
                    self.load_chunk(chunk_x, chunk_y)

    def _getblock_from(self, blocks, x, y):
        if not self.within_bounds(x, y):
            return
        
        return blocks[y][x]

    def set_block_layer(self, x, y, layer, id):
        if not 0 <= layer < 3:
            print(f'Error: invalid layer: {layer}')
        
        self._setblock_into(
            (self.foreground, self.midground, self.background)[layer],
            x, y, id)

    def get_block_layer(self, x, y, layer):
        if not 0 <= layer < 3:
            print(f'Error: invalid layer: {layer}')
        
        return self._setblock_into(
            (self.foreground, self.midground, self.background)[layer],
            x, y)
    
    def set_fg_block(self, x, y, id):
        self._setblock_into(self.foreground, x, y, id)

    def set_mg_block(self, x, y, id):
        self._setblock_into(self.midground, x, y, id)

    def set_bg_block(self, x, y, id):
        self._setblock_into(self.background, x, y, id)

    def get_fg_block(self, x, y):
        return self._getblock_from(self.foreground, x, y)

    def get_mg_block(self, x, y):
        return self._getblock_from(self.midground, x, y)

    def get_bg_block(self, x, y):
        return self._getblock_from(self.background, x, y)

    def within_bounds(self, x, y):
        return 0 <= x < self.WORLD_WIDTH and 0 <= y < self.WORLD_HEIGHT
    
    def get_tiles(self, x, y):
        if not self.within_bounds(x, y):
            return ()
        else:
            result = ()
            
            bg = self.background[y][x]
            mg = self.midground[y][x]
            fg = self.foreground[y][x]
            
            if bg is not None:
                result += (bg,)
            if mg is not None:
                result += (mg,)
            if fg is not None:
                result += (fg,)
                
            return result

    def chunk_pos(self, x, y):
        x = int(x / block.Block.WIDTH / self.CHUNK_WIDTH)
        y = int(y / block.Block.HEIGHT / self.CHUNK_HEIGHT)

        return x, y

    def update(self, dtime):
        self.ticker.update(dtime)
        
        info = pg.display.Info()
        cam_x, cam_y = self.camera.get_position()

        left, top = self.chunk_pos(cam_x, cam_y)

        left -= 2
        top -= 2

        left, top = self.bound_chunk_position(left, top)

        right = left + int(info.current_w / block.Block.WIDTH / self.CHUNK_WIDTH) + 4
        bottom = top + int(info.current_h / block.Block.HEIGHT / self.CHUNK_HEIGHT) + 4

        right, bottom = self.bound_chunk_position(right, bottom)

        for y in range(top, bottom+1):
            for x in range(left, right+1):
                self.load_chunk(x, y)

        for chunk in self.chunks_loaded:
            if chunk.deltimer(dtime):
                self.del_chunk(*self.chunk_pos(chunk.rect.x, chunk.rect.y))

    def bound_chunk_position(self, x, y):
        x = max(0, min(self.chunks_x-1, x))
        y = max(0, min(self.chunks_y-1, y))

        return (x, y)

    def load_chunk(self, x, y):
        if self.chunks[y][x] is not None:
            return

        c = Chunk(self, 
                  x*self.CHUNK_WIDTH, y*self.CHUNK_HEIGHT,
                  self.CHUNK_WIDTH, self.CHUNK_HEIGHT)
        self.chunks[y][x] = c

        self.chunks_loaded.append(c)

    def del_chunk(self, x, y):
        c = self.chunks[y][x]

        if c is None:
            return

        self.chunks[y][x] = None

        self.chunks_loaded.remove(c)

    @classmethod
    def block_by_id(cls, id, x, y):
        """Initialize required block by id at given position"""
        return None if id == 0 else block.Block.by_id(id)(x, y)

    @classmethod
    def id_from_block(cls, block):
        if block is None:
            return 0
        return block.ID

    @classmethod
    def get(cls):
        return cls.instance

    @classmethod
    def set(cls, instance):
        cls.instance = instance
