import pygame as pg

import game.texture as textures
import game.sound as sounds

from activity.activity import Activity, newactivity
from activity.main_menu_activity import MainMenuActivity

from ui.overlay import Overlay


if not pg.get_init():
    pg.init()
    pg.fastevent.init()


class App:
    WIN_WIDTH = 800
    WIN_HEIGHT = 640

    FONT = pg.font.Font('resources/fonts/dpcomic.ttf', 30)

    instance = None

    def __init__(self):
        self.set(self)

        self.frame_rate = 60

        self.screen = pg.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT), pg.DOUBLEBUF)

        pg.display.set_caption("Terrarium")

        textures.load()
        sounds.load()

        newactivity(MainMenuActivity)

    def run(self):
        timer = pg.time.Clock()

        last_update_time = pg.time.get_ticks()

        while True:
            if self.frame_rate > 0:
                timer.tick(self.frame_rate)

            t = pg.time.get_ticks()

            dtime = (t-last_update_time) / 1000.0

            last_update_time = t

            for event in pg.fastevent.get():
                Activity.current.on_event(event)

            textures.update_animation(dtime)

            Activity.current.update(dtime)

            Activity.current.draw(self.screen)

            pg.display.set_caption(f"Terrarium (fps: {int(timer.get_fps())})")

            if Overlay.instance is not None:
                Overlay.instance.draw(self.screen)

            pg.display.flip()

    def set_frame_rate(self, value):
        """Set frame rate. If value < 0, it disables timer.tick()"""
        self.frame_rate = value

    @classmethod
    def get(cls):
        return cls.instance

    @classmethod
    def set(cls, instance):
        cls.instance = instance
