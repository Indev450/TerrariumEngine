from game.item import Item
from game.texture import gettexture
from game.block import place_fg_block, place_fg_block_keep

from mods.manager import modpath


class DebugPick(Item):
    ID = 'testing:debug_pick'
    image = gettexture(modpath('textures/items/tools/debug_pick.png'))


DebugPick.on_press = place_fg_block('std:air', consume=False, force=True)
DebugPick.on_keep_press = place_fg_block_keep('std:air', consume=False, force=True)

DebugPick.register()
