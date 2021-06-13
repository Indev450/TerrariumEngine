import pygame as pg

from .sound import getsound

from config import getcfg


config = getcfg()


class MusicEntry:
    
    def __init__(self, music, priority):
        self.music = music
        self.priority = priority
    
    def __gt__(self, other):
        return self.priority > other.priority
    
    def __lt__(self, other):
        return other > self


class MusicPlayer:
    instance = None
    
    VOLUME = config["volume.music"]
    
    def __init__(self, fadeout_time=1000):
        self.current = None
        self.playing = []
        self.fadeout_time = fadeout_time
    
    def play(self, music, priority=1):
        """Add new music entry"""
        self.playing.append(MusicEntry(music, priority))
        self.playing.sort()
        
        if self.current is not self.playing[0]:
            if self.current is not None:
                self.current.music.sound.fadeout(self.fadeout_time)
            
            self.current = self.playing[0]
            
            self.current.music.sound.set_volume(self.VOLUME)
            self.current.music.sound.play(loops=-1)
    
    def stop(self, fadeout=True, replace=False):
        """Stop current music. If fadeout is True, use fadeout(), otherwise stop().
        If replace is True, start playing next entry according to priority, otherwise do nothing."""
        if self.current is None:
            return

        if fadeout:
            self.current.music.sound.fadeout(self.fadeout_time)
        else:
            self.playing.music.sound.stop()
        
        self.current = None
        self.playing = self.playing[1:]
        
        if replace and self.playing:
            self.current = self.playing[0]
            
            self.current.music.sound.play(loops=-1)

    @classmethod
    def new(cls, fadeout_time=1000):
        cls.instance = cls(fadeout_time=fadeout_time)
        return cls.instance

    @classmethod
    def get(cls):
        return cls.instance
