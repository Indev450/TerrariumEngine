from activity.activity import getactivity

from game.interactive_block import interactive
from game.block import Block

from game.texture import gettexture

from mods.manager import modpath


@interactive
class Anvil(Block):
    id = "std:anvil"
    
    inventory_image = tile = gettexture(modpath('textures/blocks/anvil.png'))
    
    layer = 1
    
    drops = [id]
    
    def on_interact(player):
        getactivity().show_craft_menu('std:anvil')


class AnvilEntity(Anvil.entity):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.add_tag('destructable')
    
    def on_destructed(self):
        self.world.set_block(*self.block, Anvil.layer, 0)


Anvil.entity = AnvilEntity
