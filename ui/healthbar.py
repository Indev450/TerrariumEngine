import pygame as pg

import app

from .element import UIElement


class HealthBar(UIElement):
    
    def __init__(self, player,
                 children=None,
                 parent=None,
                 position=(0, 0),
                 size=(100, 100)):
        super().__init__(children=children,
                         parent=parent,
                         position=position,
                         size=size)
        
        self.player = player
        self.healthbar_rect = pg.Rect(position, size)
    
    def draw(self, screen):
        self.healthbar_rect.width = self.rect.width * self.player.hp / self.player.max_hp
        
        text_sf = app.App.FONT.render(f"{self.player.hp}/{self.player.max_hp}", True, "#FFFFFF")
        
        pg.draw.rect(screen, "#222222", self.rect)
        pg.draw.rect(screen, "#FF3333", self.healthbar_rect)
        
        screen.blit(text_sf, (self.rect.x + self.rect.width/2 - text_sf.get_width()/2,
                              self.rect.y + self.rect.height/2 - text_sf.get_height()/2))
