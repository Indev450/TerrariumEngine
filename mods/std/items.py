from pygame.math import Vector2

from game.texture import gettexture

from game.item import Item
from game.block import Block
from game.entity_manager import EntityManager

from mods.manager import modpath

from utils.items import do_break_blocks_keep, do_cooldown

from .tree_api import do_chop_tree_keep


class CopperPick(Item):
    ID = 'std:copper_pick'
    image = gettexture(modpath('textures/items/copper_pick.png'))
    
    dig_damage = 1
    level = 1
    
    on_keep_press = do_break_blocks_keep(radius=6, speed=3, break_radius=1.5)
    alt_on_keep_press = do_break_blocks_keep(radius=6, speed=3, break_radius=1.5, layer=2)


class CopperAxe(Item):
    ID = 'std:copper_axe'
    image = gettexture(modpath('textures/items/copper_axe.png'))
    
    on_keep_press = do_chop_tree_keep(radius=4, speed=2)


class IronPick(Item):
    ID = 'std:iron_pick'
    image = gettexture(modpath('textures/items/iron_pick.png'))
    
    dig_damage = 1
    level = 2
    
    on_keep_press = do_break_blocks_keep(radius=6, speed=4, break_radius=1.5)
    alt_on_keep_press = do_break_blocks_keep(radius=6, speed=4, break_radius=1.5, layer=2)


class IronAxe(Item):
    ID = 'std:iron_axe'
    image = gettexture(modpath('textures/items/iron_axe.png'))
    
    on_keep_press = do_chop_tree_keep(radius=4, speed=3)


class Hammer(Item):
    ID = 'std:hammer'
    image = gettexture(modpath('textures/items/hammer.png'))
    
    radius = 4
    cooldown = do_cooldown(0.5)
    
    @classmethod
    def on_press(cls, player, itemstack, position):
        if (Vector2(player.rect.center).distance_to(Vector2(position)) > cls.radius * Block.WIDTH
            or not cls.cooldown(player)):
            return
        
        manager = EntityManager.get()
        
        for entity in manager.get_tagged_entities('destructable'):
            if entity.rect.collidepoint(position):
                entity.on_destructed()
                return


def register_items():
    CopperPick.register()
    CopperAxe.register()
    IronPick.register()
    IronAxe.register()
    Hammer.register()
