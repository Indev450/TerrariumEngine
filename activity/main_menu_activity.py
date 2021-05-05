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
from ui.textinput_label import TextInputLabel
from ui.textinput import TextInput
from ui.scrollable_label import ScrollableLabel

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
        
        self.found_worlds_holder = None

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
        # Main Menu
        root = Label(
            text="Main Menu",
            position_f=(0.25, 0.1),
            size_f=(0.5, 0.65))

        Button(
            parent=root,
            on_pressed=Call(exit, 0),
            text="exit",
            position_f=(0.25, 0.65),
            size_f=(0.5, 0.22))

        Button(
            parent=root,
            on_pressed=self.show_select,
            text="Continue",
            position_f=(0.25, 0.4),
            size_f=(0.5, 0.22))

        Button(
            parent=root,
            on_pressed=self.show_newworld,
            text="New World",
            position_f=(0.25, 0.15),
            size_f=(0.5, 0.22))

        self.overlay.add_element("mainmenu", root, True)
        
        ################################################################
        # Message
        message = Label(
            position_f=(0.25, 0.1),
            size_f=(0.5, 0.5))

        Button(
            parent=message,
            on_pressed=self.hide_message,
            text="OK",
            position_f=(0.4, 0.8),
            size_f=(0.2, 0.1))

        self.overlay.add_element("message", message)
        
        ################################################################
        # New World
        newworld = Label(
            text="New World",
            position_f=(0.25, 0.1),
            size_f=(0.5, 0.65))
        
        textinput = TextInput(
            self.app.FONT,
            on_return=lambda text: None,  # Do nothing
            max_length=20,
            prompt="Enter world name...")
        
        TextInputLabel(
            textinput,
            parent=newworld,
            textinput_offset=(0.1, 0.3),
            position_f=(0.25, 0.15),
            size_f=(0.5, 0.22))
        
        Button(
            parent=newworld,
            on_pressed=Call(self.run_mapgen, textinput),
            text="Generate",
            position_f=(0.25, 0.4),
            size_f=(0.5, 0.22))
        
        Button(
            parent=newworld,
            on_pressed=self.hide_newworld,
            text="Cancel",
            position_f=(0.25, 0.65),
            size_f=(0.5, 0.22))
        
        self.overlay.add_element("newworld", newworld)
        
        ################################################################
        # Continue
        select = Label(
            text="Select world",
            position_f=(0.25, 0.1),
            size_f=(0.5, 0.65))
        
        Button(
            parent=select,
            on_pressed=self.hide_select,
            text="Cancel",
            position_f=(0.25, 0.65),
            size_f=(0.5, 0.22))
        
        self.found_worlds_holder = ScrollableLabel(
            parent=select,
            position_f=(0.1, 0.1),
            size_f=(0.8, 0.5))
        
        if not os.path.isdir('saves') or not os.listdir('saves'):
            self.found_worlds_holder.set_text('There is no any world')
        else:
            self.find_worlds()
        
        self.overlay.add_element("selectworld", select)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.parallax.draw(screen)
    
    def find_worlds(self):
        self.found_worlds_holder.children = []
        self.found_worlds_holder.scroll = 0
        
        count = 0
        for file in os.listdir('saves'):
            if os.path.isdir(f'saves/{file}'):
                world = Button(
                    parent=self.found_worlds_holder,
                    on_pressed=Call(self.run_world, file),
                    text=file,
                    size_f=(0.8, 0.2),
                    position_f=(0.1, 0.1 + 0.3*count),
                )
                count += 1
        self.found_worlds_holder.max_scroll = (self.found_worlds_holder.get_height()*0.3*count
                                               + self.found_worlds_holder.get_height()*0.1
                                               - self.found_worlds_holder.get_height())

    def run_mapgen(self, frominput):
        # TODO - add ability to choose map generator
        
        mgconfig = get_config()["mapgens"].get(config["mapgen.selected"])
        
        path = frominput.text
        
        if not path:
            return

        self.hide_newworld()  # Hide 'new world' label

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
                         self.parallax, mapgen_t, path, *config["mapgen.world_size"])
            self.find_worlds()  # Add new world
        except Exception as e:
            logging.exception("run_mapgen():")
            self.show_message(f"{type(e).__name__}: {str(e)}")

    def run_world(self, name):
        self.hide_select()  # Hide 'select' label
        
        if not check_save_path(name):
            return self.show_message("Save file not found")

        try:
            newactivity(GameActivity, name)
        except Exception as e:
            logging.exception("run_world():")
            self.show_message(f"{type(e).__name__}: {str(e)}")

    def show_message(self, message):
        print(message)
        self.overlay.hide("mainmenu")
        self.overlay.get("message").set_text(message)
        self.overlay.show("message")

    def hide_message(self):
        self.overlay.hide("message")
        self.overlay.show("mainmenu")
    
    def show_newworld(self):
        self.overlay.hide("mainmenu")
        self.overlay.show("newworld")
    
    def hide_newworld(self):
        self.overlay.hide("newworld")
        self.overlay.show("mainmenu")
    
    def show_select(self):
        self.overlay.hide("mainmenu")
        self.overlay.show("selectworld")
    
    def hide_select(self):
        self.overlay.hide("selectworld")
        self.overlay.show("mainmenu")
