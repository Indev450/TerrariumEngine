import os
import sys
import logging
import importlib

import pygame as pg

from .activity import Activity, newactivity, getactivity
from .game_activity import GameActivity
from .mapgen_activity import MapgenActivity

from utils.calls import Call

from ui.button import Button
from ui.label import Label

from runmapgen import get_config

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

    def run_mapgen(self):
        # TODO - add ability to choose map generator
        import game.stdblocks  # TODO - turn standart things into mods
        # There are many things to do :)
        
        config = get_config()
        
        mgconfig = config["mapgens"].get("mapgenv1")

        if mgconfig is None:
            self.show_message('default mapgen not found')
            return
        
        try:
            mapgen_t = importlib.import_module(mgconfig['module']).get_mapgen()
        except ModuleNotFoundError:
            self.show_message('default mapgen not found')
            return

        try:
            newactivity(MapgenActivity, self, mapgen_t, [], 'world.tworld', 1000, 500)
        except Exception as e:
            logging.exception("run_mapgen():")
            self.show_message(f"{type(e).__name__}: {str(e)}")

    def show_message(self, message):
        print(message)
        self.overlay.hide("mainmenu")
        self.overlay.get("message").set_text(message)
        self.overlay.show("message")

    def run_world(self):
        try:
            file = open('world.tworld', 'rb')
        except FileNotFoundError:
            return self.show_message("Save file not found")

        try:
            newactivity(GameActivity, *decode(file.read()))
        except Exception as e:
            logging.exception("run_mapgen():")
            activity = newactivity(MainMenuActivity)
            getactivity().show_message(f"{type(e).__name__}: {str(e)}")

        file.close()

    def hide_message(self):
        self.overlay.hide("message")
        self.overlay.show("mainmenu")
