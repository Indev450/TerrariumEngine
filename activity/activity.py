import pygame as pg

from ui.overlay import newoverlay

import app

class Activity:
    """Activity controls game logic, can handle pygame events, etc
    
    This class contains reference to curent activity which will be rendered
    by the App class.
    """

    current = None

    def __init__(self):
        self.allowed_events = []
        
        self.app = app.App.get()

        self.overlay = newoverlay()
        
        self.allow_event(pg.QUIT)
        self.allow_event(pg.MOUSEBUTTONUP)
        self.allow_event(pg.MOUSEBUTTONDOWN)
    
    def allow_event(self, etype):
        """Allow some pygame event"""
        if etype in self.allowed_events:
            print(f"{type(self)}: event {etype} already enabled")
        self.allowed_events.append(etype)

    def disallow_event(self, etype):
        """Disable some pygame event"""
        try:
            self.allowed_events.remove(etype)
        except ValueError:
            print(f"{type(self)}: event {etype} already disabled")

    def on_begin(self):
        """Called when activity created though newactivity()"""
        pg.event.set_allowed(self.allowed_events)

    def update(self, dtime):
        """Called every frame, dtime is a time elapsed since
        last update was called"""
        pass

    def draw(self, screen):
        """Draw some activity content, like background, entities,
        blocks, etc"""
        pass

    def on_event(self, event):
        """Called for each event from pygame.event.get()"""
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
        """Called when activity was replaced by another one
        (in newactivity() or setactivity())"""
        pass


def getactivity():
    """Get current activity"""
    return Activity.current


def newactivity(type_, *args, **kwargs):
    """Create and set activity of given type,
    returns new created activity"""
    current = getactivity()

    if current is not None:
        current.on_end()

    activity = type_(*args, **kwargs)
    
    Activity.current = activity
    
    activity.on_begin()


def setactivity(activity):
    """Sets already created activity. Remember that you should re-initialize
    activitys overay and ui (i'll fix that later)"""
    current = getactivity()

    if current is not None:
        current.on_end()

    Activity.current = activity
