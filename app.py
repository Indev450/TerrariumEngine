import time

import pygame as pg

from game.world import World
from game.player import Player
from game.camera import Camera
from game.block import Block

import game.texture as textures

from activity.activity import Activity, newactivity
from activity.main_menu_activity import MainMenuActivity

from ui.overlay import Overlay
from ui.element import UIElement

import game.stdblocks  # TODO - turn standart things into mods

pg.init()

class App:
    WIN_WIDTH = 1024
    WIN_HEIGHT = 840

    FONT = pg.font.Font('resources/fonts/dpcomic.ttf', 30)

    instance = None

    def __init__(self):
        self.set(self)

        self.frame_rate = 60

        self.screen = pg.display.set_mode((self.WIN_WIDTH, self.WIN_HEIGHT))

        pg.display.set_caption("Terraclone")

        textures.load()

        newactivity(MainMenuActivity)

    def run(self):
        timer = pg.time.Clock()

        last_update_time = pg.time.get_ticks()

        while True:
            if self.frame_rate > 0:
                timer.tick(self.frame_rate)

            t = pg.time.get_ticks()

            dtime = (t-last_update_time) / 1000.0  # TODO - use actual delta time

            last_update_time = t

            for event in pg.event.get():
                Activity.current.on_event(event)

            textures.update_animation(dtime)

            Activity.current.update(dtime)

            Activity.current.draw(self.screen)

            if Overlay.instance is not None:
                Overlay.instance.draw(self.screen)

            pg.display.update()

    def set_frame_rate(self, value):
        """Set frame rate. If value < 0, it disables timer.tick()"""
        self.frame_rate = value

    @classmethod
    def get(cls):
        return cls.instance

    @classmethod
    def set(cls, instance):
        cls.instance = instance
