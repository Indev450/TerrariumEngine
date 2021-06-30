from random import uniform

from activity.activity import getactivity

from game.texture import gettexture

from game.entity import Entity
from game.block import Block
from game.inventory import Inventory

from mods.manager import modpath


class Chest(Entity):
    ID = 'std:chest'
    
    SIZE = (16, 16)
    
    TEXTURE = gettexture(modpath('textures/entities/chest.png'))
    
    @classmethod
    def from_save(cls, manager, uuid, save):
        chest = super().from_save(manager, uuid, save)
        
        chest.inventory.load(save['data']['inventory'])
        
        return chest
    
    def __init__(self,
                 manager=None,
                 uuid=None,
                 position=(0, 0),
                 velocity=(0, 0)):
        super().__init__(
            manager=manager,
            uuid=uuid,
            position=position,
            velocity=(0, 0),
            size=self.SIZE)
        
        self.inventory = Inventory(self)
        self.inventory.set_size('main', 8*4)
        
        self.checkblock = (position[0]//Block.WIDTH, position[1]//Block.HEIGHT + 1)
        
        self.add_tag('interactive')
        self.add_tag('destructable')
        
        self.image = self.TEXTURE

    def update(self, dtime):
        if self.world.get_fg_block(*self.checkblock) is None:
            self.on_destructed()
    
    def on_destructed(self):
        for drop in self.inventory.data['main']:
            ientity, _ = self.manager.newentity('builtin:item_entity', None,
                                                position=self.rect.center,
                                                velocity=(uniform(-2, 2), uniform(-2, 0)))
            
            ientity.set_item_stack(drop)
        
        self.manager.delentity(self.uuid)
    
    def on_interact(self, player):
        getactivity().open_inventory(self.inventory, 'main', 8)
    
    def on_save(self):
        return {'inventory': self.inventory.dump()}
