import pygame as pg

from game.block import Block
from game.player import Player
from game.camera import Camera
from game.world import World

from worldfile.worldfile import encode

from .activity import Activity


class GameActivity(Activity):
    BG_COLOR = pg.Color('#5555FF')

    def __init__(self, blocks):
        super().__init__()

        Block.sort_registered_entries()

        Camera.init()

        self.background = pg.Surface((self.app.WIN_WIDTH, self.app.WIN_HEIGHT))
        self.background.fill(self.BG_COLOR)

        self.world = World(blocks)

        self.player = Player()

        self.camera = Camera.get()
        self.camera.set_obj(self.player)
        self.camera.set_offset(self.app.WIN_WIDTH/2, self.app.WIN_HEIGHT/2)

        self.controls = {
            'left': False,
            'right': False,
            'up': False,
        }

        self.paused = False

    def update(self, dtime):
        if not self.paused:
            self.player.update_presses(**self.controls)
            self.player.update(dtime)

            self.world.update(dtime)

            self.camera.update_position()

    def draw(self, screen):
        objects_drawn = 0

        screen.blit(self.background, (0, 0))  # Doesn't count

        objects_drawn += self.player.draw(screen)

        objects_drawn += self.world.draw(screen)

        return objects_drawn

    def pause(self):
        self.overlay.show('pause')
        self.paused = True

    def play(self):
        self.overlay.hide('pause')
        self.paused = False

    def on_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                self.controls['left'] = True
            elif event.key == pg.K_d:
                self.controls['right'] = True
            elif event.key == pg.K_SPACE:
                self.controls['up'] = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_a:
                self.controls['left'] = False
            elif event.key == pg.K_d:
                self.controls['right'] = False
            elif event.key == pg.K_SPACE:
                self.controls['up'] = False
        elif event.type == pg.MOUSEBUTTONDOWN and not self.overlay.is_visible():
            if event.button == 1:
                x, y = event.pos
                cam_x, cam_y = self.camera.get_position()
                x += cam_x
                y += cam_y
                x = int(x/Block.WIDTH)
                y = int(y/Block.HEIGHT)
                self.world.setblock(x, y, 0)
            elif event.button == 3:
                x, y = event.pos
                cam_x, cam_y = self.camera.get_position()
                x += cam_x
                y += cam_y
                x = int(x/Block.WIDTH/World.CHUNK_WIDTH)
                y = int(y/Block.HEIGHT/World.CHUNK_WIDTH)
                try:
                    print(f"Chunk loaded at {x, y}:", self.world.chunks[x][y] is not None)
                except IndexError:
                    print(f"Chunk loaded at {x, y}: False")
        elif not (event.type == pg.MOUSEBUTTONUP and not self.overlay.is_visible()):
            super().on_event(event)

    def on_end(self):
        print("Saving world...")

        blocksize = int(Block.registered_count()/256) + 1

        data = encode(
            [[self.id_from_block(block) for block in line] for line in self.world.blocks],
            blocksize)
        
        file = open('world.tcworld', 'wb')
        
        file.write(data)
        
        file.close()

    @classmethod
    def id_from_block(cls, block):
        if block is None:
            return 0
        return type(block).ID
