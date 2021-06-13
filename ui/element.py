import pygame as pg

from .overlay import getoverlay


class UIElement:

    def __init__(self,
                 children=None,
                 parent=None,
                 position=(0, 0),
                 size=(100, 100)):

        self.children = children or []
        # We can't use [] as default argument, because in each new object it will be
        # same list object, so it can cause problems (it's a python problem)

        self.parent = parent
        
        if parent is not None:
            parent.add_child(self)  # Do it automaticly

        self.position = position
        self.size = size

        self.overlay = getoverlay()  # Instance of active ui overlay

        self.rect = None  # Bound rect of ui element

        self.set_rect(position, size)

        self.image = None  # drawable
        
        self.surface = None  # Surface that actually drawn

    def set_rect(self, position=(0, 0), size=(100, 100)):
        self.position = position
        self.size = size

        px = 0
        py = 0

        if self.parent is not None:
            px = self.parent.rect.x
            py = self.parent.rect.y
        
        self.rect = pg.Rect(
            position[0] + px,
            position[1] + py,
            *size)
    
    def on_missclick(self):
        for child in self.children:
            child.on_missclick()

    def on_click(self, position):
        for child in self.children:
            if child.rect.collidepoint(*position):
                child.on_click(position)
            else:
                child.on_missclick()

    def on_release(self, position):
        for child in self.children:
            child.on_release(position)

    def on_scroll(self, position, up):
        for child in self.children:
            if child.rect.collidepoint(*position):
                child.on_scroll(position, up)

    def update_image(self):
        self.image = pg.transform.scale(self.image, self.rect.size)

    def draw(self, screen):
        self.surface = self.image.copy()
        
        for child in self.children:
            child.draw(self.surface)

        screen.blit(self.surface, self.position)

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def set_parent(self, parent):
        self.parent = parent

    def get_width(self):
        return self.rect.width

    def get_height(self):
        return self.rect.height
