import pygame as pg

import game.texture as textures
import game.sound as sounds

from game.music import MusicPlayer

from activity.activity import getactivity, pushactivity
from activity.main_menu_activity import MainMenuActivity

from ui.overlay import Overlay

from config import getcfg


if not pg.get_init():
    pg.init()
    pg.fastevent.init()

if not pg.mixer.get_init():
    pg.mixer.init()


config = getcfg()


class App:
    WIN_WIDTH = config["app.resolution"][0]
    WIN_HEIGHT = config["app.resolution"][1]

    FONT = pg.font.Font(config["app.font"], config["app.font.size"])

    instance = None

    def __init__(self):
        self.set(self)

        self.frame_rate = config["app.maxfps"]

        self.screen = pg.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT), pg.DOUBLEBUF)

        pg.display.set_caption(config["app.caption"])

        textures.load()
        sounds.load()
        
        self.music_player = MusicPlayer.new()
        
        self.textinput = None

        pushactivity(MainMenuActivity)

    def run(self):
        timer = pg.time.Clock()

        last_update_time = pg.time.get_ticks()

        while True:
            if self.frame_rate > 0:
                timer.tick(self.frame_rate)

            t = pg.time.get_ticks()

            dtime = (t-last_update_time) / 1000.0

            last_update_time = t

            textures.update_animation(dtime)
            
            activity = getactivity()
            
            if self.textinput is not None:
                self.textinput.update(dtime)
            
            if activity is not None:
                for event in pg.fastevent.get():
                    if self.textinput is None or self.textinput.handle_event(event) is not None:
                        activity.on_event(event)

                activity.update(dtime)

                activity.draw(self.screen)
                
                if activity.overlay is not None:
                    activity.overlay.draw(self.screen)

            pg.display.set_caption(f"{config['app.caption']} (fps: {int(timer.get_fps())})")

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
