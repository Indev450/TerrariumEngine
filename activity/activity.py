import pygame as pg

from ui.overlay import newoverlay

import app


class Activity:
    """Activity controls game logic, can handle pygame events, etc
    
    This class contains reference to curent activity which will be rendered
    by the App class.
    """
    current = []
    
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
        """Called when activity created though newactivity() or pushactivity()"""
        pg.event.set_allowed(self.allowed_events)
    
    def on_stop(self):
        """Called when pushactivity() adds new activity, but this activity
        is still alive"""
        pass
    
    def on_resume(self):
        """Called when popactivity() sets this activity as main"""
        pass

    def on_end(self):
        """Called when activity was replaced or destroyed
        (in newactivity() or popactivity())"""
        pass

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
                self.overlay.on_scroll(event.pos, up=(event.button == 4))

        elif event.type == pg.MOUSEBUTTONUP and self.overlay.is_enabled():
            if event.button == 1:
                self.overlay.on_release(event.pos)


def getactivity():
    """Get current activity"""
    if len(Activity.current) > 0:
        return Activity.current[-1]


def pushactivity(type_, *args, **kwargs):
    """Create new activity of given type and push it in Activity.current.
    
    Returns new activity"""
    current = getactivity()

    if current is not None:
        current.on_stop()

    activity = type_(*args, **kwargs)
    
    activity.on_begin()
    
    Activity.current.append(activity)
    
    return activity


def popactivity():
    """Pop activity from Activity.current list."""
    current = getactivity()

    if current is not None:
        current.on_end()
        Activity.current.pop()
    else:
        return
    
    current = getactivity()
    
    if current is not None:
        current.on_resume()


def newactivity(type_, *args, **kwargs):
    """Create new activity of given type and replace current."""
    popactivity()
    
    pushactivity(type_, *args, **kwargs)
