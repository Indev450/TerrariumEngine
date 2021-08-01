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

from utils.calls import Call, WeakCall
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
        
        win_width, win_height = config["app.resolution"]

        ################################################################
        # Main Menu
        root = Label(
            text="Main Menu",
            position=(50, config["app.resolution"][1] - 50 - 440),
            size=(300, 440))

        Button(
            parent=root,
            on_pressed=WeakCall(self.show_newworld),
            text="New World",
            position=(70, 60),
            size=(160, 80))

        Button(
            parent=root,
            on_pressed=WeakCall(self.show_select),
            text="Continue",
            position=(70, 150),
            size=(160, 80))
        
        Button(
            parent=root,
            on_pressed=lambda: None,  # Do nothing
            text="Settings",
            position=(70, 240),
            size=(160, 80))

        Button(
            parent=root,
            on_pressed=Call(exit, 0),
            text="Exit",
            position=(70, 330),
            size=(160, 80))

        self.overlay.add_element("mainmenu", root, True)
        
        ################################################################
        # Message
        message = Label(
            position=(win_width//2 - 250, win_height/2 - 100),
            size=(500, 200))

        Button(
            parent=message,
            on_pressed=WeakCall(self.hide_message),
            text="OK",
            position=(200, 140),
            size=(100, 50))

        self.overlay.add_element("message", message)

        ################################################################
        # New World
        newworld = Label(
            text="New World",
            position=(win_width//2 - 250, win_height/2 - 220),
            size=(500, 440))
        
        textinput = TextInput(
            self.app.FONT,
            max_length=20,
            prompt="Enter world name...")
        
        TextInputLabel(
            textinput,
            parent=newworld,
            textinput_offset=(20, 25),
            position=(80, 60),
            size=(340, 80))
        
        Button(
            parent=newworld,
            on_pressed=WeakCall(self.run_mapgen, textinput),
            text="Generate",
            position=(150, 165),
            size=(200, 100))
        
        Button(
            parent=newworld,
            on_pressed=WeakCall(self.hide_newworld),
            text="Cancel",
            position=(150, 300),
            size=(200, 100))
        
        self.overlay.add_element("newworld", newworld)
        
        ################################################################
        # Continue
        select = Label(
            text="Select world",
            position=(win_width//2 - 250, win_height/2 - 220),
            size=(500, 440))
        
        Button(
            parent=select,
            on_pressed=WeakCall(self.hide_select),
            text="Cancel",
            position=(150, 300),
            size=(200, 100))
        
        self.found_worlds_holder = ScrollableLabel(
            parent=select,
            position=(50, 60),
            size=(400, 220))
        
        if not os.path.isdir('saves') or not os.listdir('saves'):
            self.found_worlds_holder.set_text('There is no any world')
        else:
            self.find_worlds()
        
        self.overlay.add_element("selectworld", select)
    
    def on_begin(self):
        super().on_begin()
        self.app.music_player.play(self.BG_MUSIC)
    
    def on_end(self):
        try:
            self.app.music_player.stop()
        except pg.error:
            pass  # When closing game, pygame.mixer becomes not initialized

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
                    on_pressed=WeakCall(self.run_world, file),
                    text=file,
                    size=(300, 60),
                    position=(50, 20 + 80*count),
                )
                count += 1
        self.found_worlds_holder.max_scroll = (80*count + 20 - 220)

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
