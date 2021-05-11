from game.item import Item
from game.texture import gettexture
from game.sound import getsound
from game.block import place_mg_block, place_mg_block_keep

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


class TerminalItem(Item):
    ID = 'testing:terminal'
    image = gettexture(modpath('textures/blocks/terminal.png'))
    
    on_press = place_mg_block('testing:terminal')
    on_keep_press = place_mg_block_keep('testing:terminal')
