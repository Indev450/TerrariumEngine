import os

from ctypes import py_object

import multiprocessing as mp

import pygame as pg

from .activity import Activity, popactivity, getactivity

from ui.label import Label

from mods.manager import getmanager

from utils.saves import create_save_path


class MapgenActivity(Activity):
    BG_COLOR = pg.Color('#5555FF')
    
    def __init__(self, mapgen_t, path, width, height):
        super().__init__()
        
        create_save_path(path)
        
        self.background = pg.Surface((self.app.WIN_WIDTH, self.app.WIN_HEIGHT))
        self.background.fill(self.BG_COLOR)
        
        self.curstatus = 'Wait...'
        self.curdone = 0.0
        
        self.status = mp.Value(py_object, self.curstatus)
        # py_object here because status string will be a new object reference every time

        self.done = mp.Value('d', self.curdone)
        
        self.mapgen = mapgen_t(getmanager().load_mods(),
                               os.path.join('saves', path),
                               width,
                               height,
                               self.status,
                               self.done)
        
        self.mapgen.start()
        
        self.init_ui()
    
    def init_ui(self):
        info = Label(text=f'{self.curstatus} {self.curdone} %',
                     position_f=(0.25, 0.25),
                     size_f=(0.5, 0.5))
        
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
    
    def on_event(self, event):
        if event.type == pg.QUIT:
            self.mapgen.kill()
        super().on_event(event)
    
    def update_info(self):
        self.overlay.get('info').set_text(f'{self.curstatus} {self.curdone:.4} %')
        
