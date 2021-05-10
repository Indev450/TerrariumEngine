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
                 position=(0, 0),
                 size=(100, 100)):
        super().__init__(children=children,
                         parent=parent,
                         position=position,
                         size=size)

        self.on_pressed = on_pressed
        
        self.is_pressed = False

        self.text = text

        self.image = self.get_image(text=text)

    def on_click(self, position):
        self.image = self.get_image(pressed=True, text=self.text)
        
        self.is_pressed = True

    def on_release(self, position):
        if not self.is_pressed:
            return

        if self.rect.collidepoint(*position):
            self.on_pressed()

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
