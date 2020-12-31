import pygame as pg

from .camera import Camera

import game.block as block


class Chunk:
    KEEP_ALIVE_TIME = 5

    def __init__(self, world, x, y, width, height):
        self.world = world

        size = (block.Block.WIDTH*width, block.Block.HEIGHT*height)

        self.surf = pg.Surface(size).convert_alpha()
        self.surf.fill(pg.Color(0, 0, 0, 0))

        self.x1 = x
        self.x2 = min(x+width, world.WORLD_WIDTH)

        self.y1 = y
        self.y2 = min(y+height, world.WORLD_HEIGHT)

        real_x = x * block.Block.WIDTH
        real_y = y * block.Block.HEIGHT

        real_width, real_height = size

        self.rect = pg.Rect(real_x,
                            real_y,
                            real_width,
                            real_height)

        self.alive_time = self.KEEP_ALIVE_TIME

        self.update()

    def update(self):
        self.surf.fill(pg.Color(0, 0, 0, 0))

        for y in range(self.y1, self.y2):
            for x in range(self.x1, self.x2):
                tiles = self.world.get_tiles(x, y)

                if not tiles:
                    continue
                
                image = compare_tiles(tiles)

                local_x = (x-self.x1) * block.Block.WIDTH
                local_y = (y-self.y1) * block.Block.HEIGHT

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

            return 1
        return 0


def compare_tiles(tiles):
    output = pg.Surface((block.Block.WIDTH, block.Block.HEIGHT)).convert_alpha()
    output.fill(pg.Color(0, 0, 0, 0))
    
    output.blits([(tile.image.get(), (0, 0)) for tile in tiles])

    return output
