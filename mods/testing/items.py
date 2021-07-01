import time

from pygame.math import Vector2

from game.item import Item
from game.texture import gettexture
from game.sound import getsound
from game.block import place_mg_block, place_mg_block_keep
from game.entity_manager import EntityManager
from game.melee import do_swing, do_swing_keep

from .entities import SwordSwing

from mods.std.tree_api import do_chop_tree, do_chop_tree_keep

from utils.items import do_break_blocks, do_break_blocks_keep

from mods.manager import modpath


class DebugPick(Item):
    ID = 'testing:debug_pick'
    image = gettexture(modpath('textures/items/tools/debug_pick.png'))
    
    dig_damage = 999
    level = 999  # UNLIMITED POWER!

    on_press = do_break_blocks(10, break_radius=1.5)
    on_keep_press = do_break_blocks_keep(10, 10, break_radius=1.5)


class DebugAxe(Item):
    ID = 'testing:debug_axe'
    image = gettexture(modpath('textures/items/tools/axe.png'))

    on_press = do_chop_tree(10)
    on_keep_press = do_chop_tree_keep(10, 10)
    # (ALMOST) UNLIMITED POWER!


class DebugSword(Item):
    ID = 'testing:debug_sword'
    image = gettexture(modpath('textures/items/tools/sword.png'))
    
    on_press = do_swing(SwordSwing.ID, 1/SwordSwing.TTL)
    on_keep_press = do_swing_keep(SwordSwing.ID, 1/SwordSwing.TTL)
    # (Not so) UNLIMITED POWER!


class MusicItem(Item):
    ID = 'testing:music_item'
    image = gettexture(modpath('textures/items/tools/music_item.png'))
    
    sound = getsound(modpath('sounds/items/tools/sound.wav'))
    
    @classmethod
    def on_press(cls, player, itemstack, position):
        cls.sound.play()


class Pistol(Item):
    ID = 'testing:pistol'
    image = gettexture(modpath('textures/items/tools/pistol.png'))
    
    #sound = getsound(modpath('sounds/items/pistol_shoot.wav'))
    
    _last_use_time = {}
    
    USE_TIME = 0.7
    
    @classmethod
    def on_press(cls, player, itemstack, position):
        if cls._last_use_time.get(player) is None:
            cls._last_use_time[player] = 0
            
        t = time.time()
        
        if t - cls._last_use_time[player] > cls.USE_TIME:
            cls._last_use_time[player] = t
        
        else:
            return
        
        #cls.sound.play()
        
        EntityManager.get().newentity('testing:bullet', None, 
            position=player.rect.center,
            source_entity=player,
            angle=Vector2(0, 0).angle_to(Vector2(position) - Vector2(player.rect.center)))
