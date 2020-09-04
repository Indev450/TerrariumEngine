import pygame as pg

import app

from .element import UIElement

from game.texture import gettexture


class Label(UIElement):
    background = gettexture('resources/textures/ui/label.png')

    def __init__(self,
                 text="",
                 parent=None,
                 children=None,
                 position_f=(0, 0),
                 size_f=(0.5, 0.5)):
        super().__init__(children=children,
                         parent=parent,
                         position_f=position_f,
                         size_f=size_f)

        self.image = self.get_image(text)

    def get_image(self, text=""):
        img = pg.transform.scale(self.background.get(), self.rect.size)

        text_sf = app.App.FONT.render(text, True, pg.Color('#FFFFFF'))

        img.blit(text_sf, self.get_text_pos(text_sf))

        return img

    def get_text_pos(self, text_sf):
        x = (self.rect.width-text_sf.get_width()) / 2
        y = text_sf.get_height()
        return (x, y)

    def set_text(self, text):
        self.image = self.get_image(text)
