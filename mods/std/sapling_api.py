from random import randint

from game.entity import Entity
from game.entity_manager import EntityManager
from game.item_stack import ItemStack
from game.block import Block, BlockDefHolder, BlockObstructed
from game.item import Item


class SaplingDef:
    ID = 'std:sapling'
    
    SIZE = (16, 32)
    
    TEXTURE = None
    
    ITEM_TEXTURE = None
    
    TIME_TO_GROW = (20, 50)
    
    TREE = 'std:tree'
    
    @classmethod
    def register(cls):
        Sapling, SaplingItem = make_sapling(cls)
        Sapling.register()
        SaplingItem.register()


def make_sapling(sapdef):
    class Sapling(Entity):
        ID = sapdef.ID
        
        SIZE = sapdef.SIZE
        
        TEXTURE = sapdef.TEXTURE
        
        TIME_TO_GROW = sapdef.TIME_TO_GROW
        
        TREE = sapdef.TREE
        
        @classmethod
        def from_save(cls, manager, uuid, save):
            sap = super().from_save(manager, uuid, save)
            
            sap.time_to_grow = save['data']['time_to_grow']
            
            return sap

        def __init__(self,
                     manager=None,
                     uuid=None,
                     position=(0, 0),
                     velocity=(0, 0)):
            super().__init__(
                manager=manager,
                uuid=uuid,
                position=(position[0],
                          position[1] + Block.HEIGHT - self.SIZE[1]),
                velocity=(0, 0),
                size=self.SIZE)
            
            self.image = self.TEXTURE
            
            self.block = (position[0]//Block.WIDTH, position[1]//Block.HEIGHT)
            self.checkblock = (self.block[0], self.block[1] + 1)
            
            self.time_to_grow = randint(*self.TIME_TO_GROW)
            
            self.add_tag('destructable')
            
            self.tree = BlockDefHolder.by_strid(self.TREE)
            
            self.world.set_mg_block(*self.block, 1)
        
        def update(self, dtime):
            self.time_to_grow -= dtime
            
            if self.time_to_grow <= 0:
                if self.tree.can_place(self.world, *self.block):
                    self.world.set_mg_block(*self.block, BlockDefHolder.id_by_strid(self.TREE))
                    
                    self.manager.delentity(self.uuid)
                    
                    return
                else:
                    self.time_to_grow = randint(*self.TIME_TO_GROW)
            
            if self.world.get_fg_block(*self.checkblock) is None:
                self.on_destructed()
        
        def on_destructed(self):
            ientity, _ = self.manager.newentity('builtin:item_entity', None,
                                                position=self.rect.center)
            
            ientity.set_item_stack(ItemStack.from_str(self.ID))
            
            self.world.set_mg_block(*self.block, 0)
            
            self.manager.delentity(self.uuid)
        
        def on_save(self):
            self.rect.y -= Block.HEIGHT - self.SIZE[1]
            # If dont do that, when you enter world second time saplings will
            # break because they will be higher than should be. Trees have no
            # such problem because they are not saved as entities after quit
            
            return {
                'time_to_grow': self.time_to_grow,
            }


    class SaplingItem(Item):
        ID = sapdef.ID
        
        image = sapdef.ITEM_TEXTURE
        
        @classmethod
        def on_press(cls, player, itemstack, position):
            x, y = position
            
            x = int(x//Block.WIDTH)
            y = int(y//Block.HEIGHT)
            
            if (player.world.get_fg_block(x, y) is not None or player.world.get_fg_block(x, y+1) is None
                or player.world.get_mg_block(x, y) is not None):
                return
            
            x *= Block.WIDTH
            y *= Block.HEIGHT
            
            EntityManager.get().newentity(cls.ID, None, position=(x, y))
            
            itemstack.consume_items(1)
    
    return Sapling, SaplingItem
