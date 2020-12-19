import pygame as pg

import app

from .overlay import getoverlay


class UIElement:

    def __init__(self,
                 children=None,
                 parent=None,
                 position_f=(0, 0),
                 size_f=(0.5, 0.5)):
        if children is not None:
            self.children = children
        else:
            self.children = []
        # We can't use [] as default argument, because in each new object it will be
        # same list object, so it can cause problems (it's a python problem)

        self.parent = parent
        
        if parent is not None:
            parent.add_child(self)  # Do it automaticly

        self.position_f = position_f
        self.size_f = size_f

        self.overlay = getoverlay()  # Instance of active ui overlay

        self.rect = None  # Bound rect of ui element

        self.set_rect(position_f, size_f)

        self.image = None  # drawable

    def set_rect(self, position_f=(0, 0), size_f=(0.5, 0.5)):
        pwidth = app.App.WIN_WIDTH
        pheight = app.App.WIN_HEIGHT

        px = 0
        py = 0

        if self.parent is not None and self.parent.image is not None:
            pwidth = self.parent.get_width()
            pheight = self.parent.get_height()
            px = self.parent.rect.x
            py = self.parent.rect.y

        self.rect = pg.Rect(
            pwidth*position_f[0] + px,
            pheight*position_f[1] + py,
            pwidth*size_f[0],
            pheight*size_f[1])

    def on_resize(self):
        for child in self.children:
            child.on_resize()

        self.set_rect(self.position_f, self.size_f)

        self.update_image()

    def on_click(self, position):
        for child in self.children:
            if child.rect.collidepoint(*position):
                child.on_click(position)

    def on_release(self, position):
        for child in self.children:
            child.on_release(position)

    def on_scroll(self, up):
        for child in self.children:
            child.on_scroll(up)

    def update_image(self):
        self.image = pg.transform.scale(self.image, self.rect.size)

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        for child in self.children:
            child.draw(screen)

    def add_child(self, child):
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)

    def set_parent(self, parent):
        self.parent = parent

    def get_width(self):
        if self.image is not None:
            return self.image.get_width()

    def get_height(self):
        if self.image is not None:
            return self.image.get_height()
