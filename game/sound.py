import traceback

import pygame as pg


class Sound:
    instances = {}
    
    def __init__(self, name):
        self.name = name
        self.sound = None
    
    def load(self, force=False):
        try:
            self.sound = pg.mixer.Sound(self.name)
        except pg.error as e:
            print(f"Error: could not load sound {self.name}: {e}")
            self.sound = pg.mixer.Sound(b'')
        except FileNotFoundError:
            print(f'Error: could not load sound {self.name}: no such file')
            self.sound = pg.mixer.Sound(b'')

    def play(self, *args):
        if self.sound is not None:
            self.sound.play(*args)
        else:
            traceback.print_stack()
            print(f'Error: sound {self.name} is not loaded')


def getsound(name):
    if Sound.instances.get(name):
        return Sound.instances[name]
    
    Sound.instances[name] = Sound(name)
    
    return Sound.instances[name]


def load(force=False):
    for name in Sound.instances:
        Sound.instances[name].load(force)


def reload():
    load(True)
