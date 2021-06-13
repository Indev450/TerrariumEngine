from game.texture import gettexture
from game.block import Block
from game.interactive_block import interactive

from mods.manager import modpath


@interactive
class Terminal(Block):
    id = "testing:terminal"
    
    drops = ['testing:terminal']
    
    tile = gettexture(modpath('textures/blocks/terminal.png'))
    
    inventory_image = tile
    
    layer = 1
    
    @classmethod
    def on_interact(cls, player):
        print('Hello, World!')
