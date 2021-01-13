from game.item import Item
from game.texture import gettexture
from game.sound import getsound
from game.block import place_fg_block, place_fg_block_keep

from mods.manager import modpath


class DebugPick(Item):
    ID = 'testing:debug_pick'
    image = gettexture(modpath('textures/items/tools/debug_pick.png'))

    on_press = place_fg_block('std:air', consume=False, force=True)
    on_keep_press = place_fg_block_keep('std:air', consume=False, force=True)


class MusicItem(Item):
    ID = 'testing:music_item'
    image = gettexture(modpath('textures/items/tools/music_item.png'))
    
    sound = getsound(modpath('sounds/items/tools/sound.ogg'))
    
    @classmethod
    def on_press(cls, player, itemstack, position):
        cls.sound.play()
