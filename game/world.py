import pygame as pg

from .block import Block
from .camera import Camera

class World:
    instance = None

    def __init__(self, blocks):

        self.set(self)

        print("Initializing blocks...")

        self.WORLD_WIDTH = len(blocks[0])
        self.WORLD_HEIGHT = len(blocks)

        self.blocks = [[self.block_by_id(
            blocks[y][x],
            x*Block.WIDTH,
            y*Block.HEIGHT) for x in range(self.WORLD_WIDTH)] for y in range(self.WORLD_HEIGHT)]

        self.camera = Camera.get()

    def is_collide(self, entity, on_collide):
        # block_w = 16, ent.rect.left = 128, ent.rect.right = 138, range = (8, 9)
        for x in self.worldrange_x(entity.rect.left, entity.rect.right):
            for y in self.worldrange_y(entity.rect.top, entity.rect.bottom):
                if self.blocks[y][x] is not None and pg.sprite.collide_rect(self.blocks[y][x], entity):
                    on_collide(self.blocks[y][x])

    def worldrange_x(self, x1, x2):
        return range(max(0, int(x1/Block.WIDTH)), min(int(x2/Block.WIDTH)+1, self.WORLD_WIDTH))

    def worldrange_y(self, y1, y2):
        return range(max(0, int(y1/Block.HEIGHT)), min(int(y2/Block.HEIGHT)+1, self.WORLD_HEIGHT))

    def draw(self, screen):
        info = pg.display.Info()
        cam_x, cam_y = self.camera.get_position()
        cam_x = int(cam_x/Block.WIDTH)
        cam_y = int(cam_y/Block.HEIGHT)
        left = -1
        top = -1
        right = int(info.current_w/Block.WIDTH) + 1
        bottom = int(info.current_h/Block.HEIGHT) + 1
        objects_drawn = 0
        for y in range(top, bottom):
            for x in range(left, right):
                if self.blocks[max(0, min(y+cam_y, self.WORLD_HEIGHT-1))][max(0, min(x+cam_x, self.WORLD_WIDTH-1))] is not None:
                    objects_drawn += self.blocks[max(0, min(y+cam_y, self.WORLD_HEIGHT-1))][max(0, min(x+cam_x, self.WORLD_WIDTH-1))].draw(screen)
                    # Long boi
        return objects_drawn

    def setblock(self, x, y, id):
        if x < 0 or x >= self.WORLD_WIDTH or y < 0 or y >= self.WORLD_HEIGHT:
            return
        self.blocks[y][x] = self.block_by_id(id,
            x*Block.WIDTH,
            y*Block.HEIGHT)

    @classmethod
    def block_by_id(cls, id, x, y):
        """Initialize required block by id at given position"""
        return None if id == 0 else Block.by_id(id)(x, y)

    @classmethod
    def get(cls):
        return cls.instance

    @classmethod
    def set(cls, instance):
        cls.instance = instance
