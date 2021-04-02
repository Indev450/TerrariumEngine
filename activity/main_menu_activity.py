import os
import sys
import logging
import importlib

import pygame as pg

from .activity import Activity, pushactivity, getactivity, newactivity
from .game_activity import GameActivity
from .mapgen_activity import MapgenActivity
from .default_parallax import DefaultParallax

from game.sound import getsound
from game.camera import Camera

from utils.calls import Call
from utils.saves import check_save_path

from ui.button import Button
from ui.label import Label

from runmapgen import get_config

from worldfile.worldfile import decode

from config import getcfg


config = getcfg()


class MainMenuActivity(Activity):
    BG_COLOR = pg.Color(config["menu.background"])
    
    BG_MUSIC = getsound(config["menu.music"])

    def __init__(self):
        super().__init__()

        self.background = pg.Surface((self.app.WIN_WIDTH, self.app.WIN_HEIGHT))
        self.background.fill(self.BG_COLOR)
        
        Camera.init()
        
        self.parallax = DefaultParallax()

        self.init_ui()
    
    def on_begin(self):
        super().on_begin()
        self.app.music_player.play(self.BG_MUSIC)
    
    def on_end(self):
        try:
            self.app.music_player.stop()
        except pg.error:
            pass  # When closing game, pygame.mixer becomes not initialized

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
            position_f=(0.4, 0.8),
            size_f=(0.2, 0.1))

        self.overlay.add_element("message", message)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.parallax.draw(screen)

    def run_mapgen(self):
        # TODO - add ability to choose map generator
        # TODO - add ability to choose world save path
        global config
        
        path = 'world'
        
        gamecfg = config

        config = get_config()
        
        mgconfig = config["mapgens"].get(gamecfg["mapgen.selected"])

        if mgconfig is None:
            self.show_message('default mapgen not found')
            return
        
        try:
            mapgen_t = importlib.import_module(mgconfig['module']).get_mapgen()
        except ModuleNotFoundError:
            self.show_message('default mapgen not found')
            return

        try:
            pushactivity(MapgenActivity, 
                         self.parallax, mapgen_t, path, *gamecfg["mapgen.world_size"])
        except Exception as e:
            logging.exception("run_mapgen():")
            self.show_message(f"{type(e).__name__}: {str(e)}")

    def show_message(self, message):
        print(message)
        self.overlay.hide("mainmenu")
        self.overlay.get("message").set_text(message)
        self.overlay.show("message")

    def run_world(self):
        # TODO - add ability to choose loaded world
        path = 'world'
        
        if not check_save_path(path):
            return self.show_message("Save file not found")

        try:
            newactivity(GameActivity, path)
        except Exception as e:
            logging.exception("run_world():")
            self.show_message(f"{type(e).__name__}: {str(e)}")

    def hide_message(self):
        self.overlay.hide("message")
        self.overlay.show("mainmenu")
