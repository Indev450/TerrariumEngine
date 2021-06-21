import traceback
import time

import pygame as pg

from config import getcfg


config = getcfg()


class Sound:
    instances = {}
    
    def __init__(self, name, volume=1.0, min_wait=0.1):
        self.name = name
        self.sound = None
        self.volume = volume * config["volume.sounds"]
        self.min_wait = min_wait
        self.last_played = 0
    
    def load(self, force=False):
        try:
            self.sound = pg.mixer.Sound(self.name)
            self.sound.set_volume(self.volume)
        except pg.error as e:
            print(f"Error: could not load sound {self.name}: {e}")
            self.sound = pg.mixer.Sound(b'')
        except FileNotFoundError as e:
            print(f'Error: could not load sound {self.name}: {e}')
            self.sound = pg.mixer.Sound(b'')

    def play(self, *args, **kwargs):
        if time.time() - self.last_played < self.min_wait:
            return
        
        if self.sound is not None:
            self.last_played = time.time()
            
            self.sound.play(*args, **kwargs)
        else:
            traceback.print_stack()
            print(f'Error: sound {self.name} is not loaded')


def getsound(name, volume=1.0, min_wait=0.1):
    if Sound.instances.get(name):
        return Sound.instances[name]
    
    Sound.instances[name] = Sound(name, volume, min_wait)
    
    return Sound.instances[name]


def load(force=False):
    for name in Sound.instances:
        Sound.instances[name].load(force)


def reload():
    load(True)
