from activity.activity import getactivity

from game.interactive_block import interactive
from game.block import Block

from game.texture import gettiled, animtiled

from mods.manager import modpath


@interactive
class Furnace(Block):
    id = "std:furnace"
    
    inventory_image = tile = animtiled(gettiled(modpath('textures/blocks/furnace.png'), 4, 1), {
        'idle': {
            'speed': 1.0/8,
            'tiles': [(0, 0), (1, 0), (2, 0), (3, 0)],
        },
    })
    
    layer = 1
    
    drops = [id]
    
    def on_interact(player):
        getactivity().show_craft_menu('std:furnace')


class FurnaceEntity(Furnace.entity):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.add_tag('destructable')
    
    def on_destructed(self):
        self.world.set_block(*self.block, Furnace.layer, 0)


Furnace.entity = FurnaceEntity
