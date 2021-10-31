import pygame as pg

from .scrollable_label import ScrollableLabel
from .element import UIElement
from .button import Button

from utils.calls import Call

from game.texture import gettexture
from game.craft import CraftManager

import app


class CraftUI:
    CRAFT_SIZE = (310, 70)
    ARROW = gettexture('resources/textures/ui/arrow.png')
    SPACE = 10
    
    def __init__(self, position):
        self.root = ScrollableLabel(
            position=position,
            size=(self.SPACE*3 + self.CRAFT_SIZE[0] + 100, 280))
            
        self.crafts = 'builtin:emptyhands'
    
    def set_crafts(self, player, crafts):
        import traceback
        
        self.crafts = crafts
        
        crafts = CraftManager.get().crafts.get(crafts, {})
        
        self.root.children = []
        
        space = self.SPACE
        
        y = space
        
        self.root.max_scroll = ((len(crafts) - 3)*(self.CRAFT_SIZE[1] + space))
        self.root.scroll = 0
        
        for craft in crafts.values():
            self.create_craft_ui((space, y), player, craft)
            
            Button(
                parent=self.root,
                position=(space*2 + self.CRAFT_SIZE[0], y),
                size=(100, 50),
                text='Craft',
                on_pressed=Call(self.do_craft, craft, player))
            
            y += space + self.CRAFT_SIZE[1]
    
    def update(self, player):
        scroll = self.root.scroll
        self.set_crafts(player, self.crafts)
        self.root.set_scroll(scroll)
    
    def do_craft(self, craft, player):
        craft.do_craft(player)
        self.update(player)

    def create_craft_ui(self, position, player, craft):
        missing = craft.missing_inputs(player)
        
        space = self.SPACE
        
        x = space
        y = space
        
        xcount = 0
        xcount_max = 3
        
        l = ScrollableLabel(size=self.CRAFT_SIZE, position=position, parent=self.root)
        
        l.max_scroll = ((len(craft.inputs) - 1)//xcount_max)*(50 + space)
        
        # Craft input
        for item, count in craft.get_inputs():
            el = UIElement(parent=l,
                           position=(x, y),
                           size=(50, 50))
            
            el.image = draw_item(item, count, (50, 50), (item, count) in missing)
            
            xcount += 1
            
            if xcount > xcount_max:
                xcount = 0
                x = -50
                y += 50 + space
            
            x += space + 50
        
        # Craft arrow
        el = UIElement(parent=l,
                       position=(50*3 + space*4, 10),
                       size=(50, 50))
        
        el.image = self.ARROW.get()

        # Craft output
        el = UIElement(parent=l,
                       position=(50*4 + space*5, 10),
                       size=(50, 50))
        
        el.image = draw_item(*craft.get_output(), (50, 50))


def draw_item(item, count, size, miss=False):
    surf = pg.transform.scale(item.image.get(), size)
    
    if count != 1:
        surf.blit(app.App.FONT.render(str(count), True, '#FF1111' if miss else '#FFFFFF'),
                  (size[0]*0.1, size[1]*0.1))
    
    return surf
