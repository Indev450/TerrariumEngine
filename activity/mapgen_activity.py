import os

from ctypes import py_object

import multiprocessing as mp

import pygame as pg

from .activity import Activity, popactivity, getactivity

from ui.label import Label

from mods.manager import ModManager

from utils.saves import create_save_path

from config import getcfg


config = getcfg()


class MapgenActivity(Activity):
    BG_COLOR = pg.Color('#5555FF')
    
    def __init__(self, parallax, mapgen_t, path, width, height):
        super().__init__()
        
        self.parallax = parallax  # MainMenuActivity.parallax
        
        create_save_path(path)
        
        self.background = pg.Surface((self.app.WIN_WIDTH, self.app.WIN_HEIGHT))
        self.background.fill(self.BG_COLOR)
        
        self.curstatus = 'Wait...'
        self.curdone = 0.0
        
        self.status = mp.Value(py_object, self.curstatus)
        # py_object here because status string will be a new object reference every time

        self.done = mp.Value('d', self.curdone)
        
        modmanager = ModManager.get()
        modmanager.reset_handlers()
        
        self.mapgen = mapgen_t(modmanager.load_mods(),
                               os.path.join('saves', path),
                               width,
                               height,
                               self.status,
                               self.done)
        
        self.mapgen.start()
        
        win_width, win_height = config["app.resolution"]

        info = Label(text=f'{self.curstatus} {self.curdone} %',
                     position=(win_width//2 - 250, win_height//2 - 100),
                     size=(500, 200))
        
        self.overlay.add_element('info', info, True)

    def update(self, dtime):
        need_update = False
        
        with self.status.get_lock():
            if self.status.value != self.curstatus:
                self.curstatus = self.status.value
                need_update = True

        with self.done.get_lock():
            if self.done.value != self.curdone:
                if self.done.value < 0:
                    self.mapgen.join()
                    
                    popactivity()
                    
                    activity = getactivity()
                    
                    if activity is not None:
                        activity.show_message('Map generated!')
                    
                    return

                self.curdone = self.done.value
                need_update = True

        if need_update:
            self.update_info()

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        self.parallax.draw(screen)
    
    def on_event(self, event):
        if event.type == pg.QUIT:
            self.mapgen.kill()
        super().on_event(event)
    
    def update_info(self):
        self.overlay.get('info').set_text(f'{self.curstatus} {self.curdone:.4} %')
        
