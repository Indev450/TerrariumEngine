from game.item import Item
from game.texture import gettexture
from game.sound import getsound
from utils.items import do_break_blocks, do_break_blocks_keep

from mods.manager import modpath


class DebugPick(Item):
    ID = 'testing:debug_pick'
    image = gettexture(modpath('textures/items/tools/debug_pick.png'))
    
    dig_damage = 999
    level = 999  # UNLIMITED POWER!

    on_press = do_break_blocks(10, break_radius=1.5)
    on_keep_press = do_break_blocks_keep(10, 10, break_radius=1.5)


class MusicItem(Item):
    ID = 'testing:music_item'
    image = gettexture(modpath('textures/items/tools/music_item.png'))
    
    sound = getsound(modpath('sounds/items/tools/sound.wav'))
    
    @classmethod
    def on_press(cls, player, itemstack, position):
        cls.sound.play()
