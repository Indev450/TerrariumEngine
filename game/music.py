import pygame as pg

from .sound import getsound


class MusicPlayer:
    instance = None
    
    def __init__(self, fadeout_time=1000):
        self.playing = None
        self.fadeout_time = fadeout_time
    
    def play(self, music):
        if self.playing is not None:
            self.playing.sound.fadeout(self.fadeout_time)
        
        self.playing = music
        self.playing.play(loops=-1)
    
    def stop(self, fadeout=True):
        if self.playing is None:
            return

        if fadeout:
            self.playing.sound.fadeout(self.fadeout_time)
        else:
            self.playing.sound.stop()

    @classmethod
    def new(cls, fadeout_time=1000):
        cls.instance = cls(fadeout_time=fadeout_time)
        return cls.instance

    @classmethod
    def get(cls):
        return cls.instance
