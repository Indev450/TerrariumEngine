from game.item import Item
from game.texture import gettexture
from game.block import Block, place_fg_block, place_fg_block_keep


class StoneItem(Item):
    ID = 'std:stone'
    image = gettexture('resources/textures/items/blocks/stone.png')


StoneItem.on_press = place_fg_block('std:stone')
StoneItem.on_keep_press = place_fg_block_keep('std:stone')

StoneItem.register()
