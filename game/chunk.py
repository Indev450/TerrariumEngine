import pygame as pg

from .camera import Camera

import game.block as blockm

from config import getcfg


config = getcfg()


class Chunk:
    KEEP_ALIVE_TIME = config["chunk.keep_alive_time"]

    def __init__(self, world, x, y, width, height):
        self.world = world

        size = (blockm.Block.WIDTH*width, blockm.Block.HEIGHT*height)

        self.surf = pg.Surface(size).convert_alpha()

        self.x1 = x
        self.x2 = min(x+width, world.WORLD_WIDTH)

        self.y1 = y
        self.y2 = min(y+height, world.WORLD_HEIGHT)

        real_x = x * blockm.Block.WIDTH
        real_y = y * blockm.Block.HEIGHT

        real_width, real_height = size

        self.rect = pg.Rect(real_x,
                            real_y,
                            real_width,
                            real_height)

        self.alive_time = self.KEEP_ALIVE_TIME

        self.update()
        
        for y in range(self.y1, self.y2):
            for x in range(self.x1, self.x2):
                for layer in range(0, 2):
                    block = self.world.get_block(x, y, layer)
                    
                    if block is not None:
                        block.on_load(x, y)

    def update(self):
        self.surf.fill(pg.Color(0, 0, 0, 0))

        for y in range(self.y1, self.y2):
            for x in range(self.x1, self.x2):
                tiles = self.world.get_tiles(x, y)

                if not tiles:
                    continue
                
                image = compare_tiles(tiles, x, y)

                local_x = (x-self.x1) * blockm.Block.WIDTH
                local_y = (y-self.y1) * blockm.Block.HEIGHT

                self.surf.blit(image, (local_x, local_y))

    def deltimer(self, dtime):
        self.alive_time -= dtime

        return self.alive_time <= 0

    def draw(self, screen):
        info = pg.display.Info()
        offset_x, offset_y = Camera.get().get_position()
        draw_x = self.rect.x - offset_x
        draw_y = self.rect.y - offset_y
        if (-self.rect.width <= draw_x <= info.current_w + self.rect.width and
           -self.rect.height <= draw_y <= info.current_h + self.rect.height):
            screen.blit(self.surf, (draw_x, draw_y))

            self.alive_time = self.KEEP_ALIVE_TIME


def compare_tiles(tiles, x, y):
    output = pg.Surface((blockm.Block.WIDTH, blockm.Block.HEIGHT), pg.SRCALPHA).convert_alpha()
    
    output.blits([(tile.gettile(x, y), (0, 0)) for tile in tiles])

    return output
