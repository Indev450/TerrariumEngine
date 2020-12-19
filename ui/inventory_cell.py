import pygame as pg

import app

from .element import UIElement

from game.texture import gettexture


class InventoryCell(UIElement):
    background = gettexture('resources/textures/ui/label.png')
    
    def __init__(self,
                 inventoryref,
                 children=None,
                 parent=None,
                 position_f=(0, 0),
                 size_f=(0.5, 0.5)):
        super().__init__(children=children,
                         parent=parent,
                         position_f=position_f,
                         size_f=size_f)
        self.invref = inventoryref
        self.invref().set_change_callback(self.on_change)

        self.image = self.get_image()
    
    def get_image(self):
        img = pg.transform.scale(self.background.get(), self.rect.size)

        istack = self.invref()

        if istack is not None and not istack.empty():
            itemimg = pg.transform.scale(istack.item_t.image.get(), self.rect.size)
            
            img.blit(itemimg, (0, 0))
            
            if istack.count > 1:
                text = app.App.FONT.render(
                    f'{istack.count}', True, pg.Color('#FFFFFF'))
                
                img.blit(text, (self.rect.size[0]*0.1,
                                self.rect.size[1]*0.1))
        
        return img
    
    def on_change(self, itemstack, change):
        self.image = self.get_image()
    
    def on_click(self, position):
        inv = self.invref.inventory

        inv.swap(self.invref.name, self.invref.index, 'buffer', 0)
