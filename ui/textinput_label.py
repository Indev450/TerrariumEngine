import pygame as pg

import app

from game.texture import gettexture

from .textinput import TextInput
from .element import UIElement


class TextInputLabel(UIElement):
    background = gettexture('resources/textures/ui/textinput.png')

    def __init__(self,
                 textinput,
                 textinput_offset=(0, 0),
                 parent=None,
                 children=None,
                 position=(0, 0),
                 size=(100, 100)):
        super().__init__(children=children,
                         parent=parent,
                         position=position,
                         size=size)
        self.textinput = textinput
        self.textinput.draw_cursor = False
        self.textinput.render_text()
        
        self.textinput_offset = textinput_offset
    
    def on_click(self, position):
        self.textinput.draw_cursor = True
        self.textinput.render_text()
        app.App.instance.textinput = self.textinput
    
    def on_missclick(self):
        if app.App.instance.textinput is self.textinput:
            self.textinput.draw_cursor = False
            self.textinput.render_text()
            app.App.instance.textinput = None
    
    def get_image(self):
        img = pg.transform.scale(self.background.get(), self.rect.size)
        
        self.image = img  # For self.get_width and get_height
        
        img.blit(self.textinput.surface, self.textinput_offset)
        
        return img
    
    def draw(self, screen):
        # Update image each frame
        self.image = self.get_image()
        
        super().draw(screen)
