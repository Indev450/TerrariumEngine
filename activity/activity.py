import pygame as pg

from ui.overlay import newoverlay

import app

class Activity:

    current = None

    def __init__(self):
        self.app = app.App.get()

        self.overlay = newoverlay()

    def on_begin(self):
        pass

    def update(self, dtime):
        pass

    def draw(self, screen):
        pass

    def on_event(self, event):
        if event.type == pg.QUIT:
            print("Quit message received")

            pg.quit()

            self.on_end()

            raise SystemExit(0)

        elif event.type == pg.MOUSEBUTTONDOWN and self.overlay.is_enabled():
            if event.button == 1:
                self.overlay.on_press(event.pos)
            elif event.button in (4, 5):
                self.overlay.on_scroll(up=(event.button == 4))

        elif event.type == pg.MOUSEBUTTONUP and self.overlay.is_enabled():
            if event.button == 1:
                self.overlay.on_release()

    def on_end(self):
        pass


def getactivity():
    return Activity.current


def newactivity(type_, *args, **kwargs):
    current = getactivity()

    if current is not None:
        current.on_end()

    activity = type_(*args, **kwargs)
    
    Activity.current = activity
    
    activity.on_begin()
