import pygame as pg

import app

from .element import UIElement

from game.texture import gettexture


class Button(UIElement):
    pressed_image = gettexture('resources/textures/ui/button_pressed.png')
    released_image = gettexture('resources/textures/ui/button.png')

    def __init__(self,
                 on_pressed,
                 text="",
                 children=None,
                 parent=None,
                 position_f=(0, 0),
                 size_f=(0.5, 0.5)):
        super().__init__(children=children,
                         parent=parent,
                         position_f=position_f,
                         size_f=size_f)

        self.on_pressed = on_pressed

        self.text = text

        self.image = self.get_image(text=text)

    def on_click(self, position):
        self.on_pressed()
        self.image = self.get_image(pressed=True, text=self.text)

    def on_release(self):
        self.image = self.get_image(text=self.text)

    def get_image(self, pressed=False, text=""):
        img = self.pressed_image if pressed else self.released_image
        img = pg.transform.scale(img.get(), self.rect.size)

        text_sf = app.App.FONT.render(text, True, pg.Color('#FFFFFF'))

        img.blit(text_sf, self.get_text_pos(text_sf))
        
        return img

    def get_text_pos(self, text_sf):
        x = (self.rect.width-text_sf.get_width()) / 2
        y = (self.rect.height-text_sf.get_height()) / 2
        return (x, y)