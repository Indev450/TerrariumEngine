from game.item import Item
from game.texture import gettexture
from game.block import place_fg_block, place_fg_block_keep

from mods.manager import modpath


class StoneItem(Item):
    ID = 'std:stone'
    image = gettexture(modpath('textures/items/blocks/stone.png'))


StoneItem.on_press = place_fg_block('std:stone')
StoneItem.on_keep_press = place_fg_block_keep('std:stone')

StoneItem.register()
