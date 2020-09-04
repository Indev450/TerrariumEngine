import os
import sys

import pygame as pg

from .activity import Activity, newactivity
from .game_activity import GameActivity

from utils.calls import Call

from ui.button import Button
from ui.label import Label

from worldfile.worldfile import decode


class MainMenuActivity(Activity):
    BG_COLOR = pg.Color('#5555FF')

    def __init__(self):
        super().__init__()

        self.background = pg.Surface((self.app.WIN_WIDTH, self.app.WIN_HEIGHT))
        self.background.fill(self.BG_COLOR)

        self.init_ui()

    def init_ui(self):
        root = Label(
            text="Main Menu",
            position_f=(0.25, 0.1),
            size_f=(0.5, 0.65))

        exitbutton = Button(
            parent=root,
            on_pressed=Call(exit, 0),
            text="exit",
            position_f=(0.25, 0.65),
            size_f=(0.5, 0.22))

        continue_ = Button(
            parent=root,
            on_pressed=self.run_world,
            text="Continue",
            position_f=(0.25, 0.4),
            size_f=(0.5, 0.22))

        newworld = Button(
            parent=root,
            on_pressed=self.run_mapgen,
            text="New World",
            position_f=(0.25, 0.15),
            size_f=(0.5, 0.22))

        self.overlay.add_element("mainmenu", root, True)

        message = Label(
            position_f=(0.25, 0.1),
            size_f=(0.5, 0.5))

        ok = Button(
            parent=message,
            on_pressed=self.hide_message,
            text="OK",
            position_f=(0.325, 0.5),
            size_f=(0.15, 0.1))

        self.overlay.add_element("message", message)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        return 0  # No objects drawn

    def update(self, dtime):
        pass

    def run_mapgen(self):
        os.popen(f"{sys.executable} runmapgen.py")

        self.show_message("Mapgen Started")

    def show_message(self, message):
        self.overlay.hide("mainmenu")
        self.overlay.show("message")
        self.overlay.get("message").set_text(message)

    def run_world(self):
        try:
            file = open('world.tcworld', 'rb')
        except FileNotFoundError:
            print("Error: save file not found")
            return

        newactivity(GameActivity, decode(file.read()))

        file.close()

    def hide_message(self):
        self.overlay.hide("message")
        self.overlay.show("mainmenu")
