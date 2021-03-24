import pygame as pg

from .game_object import GameObject

import game.entity_manager as entitymanager
import game.item_stack as itemstack
import game.world as worldm

from tilemap.maketilemap import tilemap_positions, flags


def get_tilemap_position(x, y, layer):
    world = worldm.World.get()
    
    block_flags = 0
    
    self = world.get_block(x, y, layer)
    
    up = world.get_block(x, y-1, layer)
    down = world.get_block(x, y+1, layer)
    left = world.get_block(x-1, y, layer)
    right = world.get_block(x+1, y, layer)
    
    block_flags |= flags['up'] if up is None or (not up.tilecomparable and up is not self) else 0
    block_flags |= flags['down'] if down is None or (not down.tilecomparable and down is not self) else 0
    block_flags |= flags['left'] if left is None or (not left.tilecomparable and left is not self) else 0
    block_flags |= flags['right'] if right is None or (not right.tilecomparable and right is not self) else 0
    
    return tilemap_positions[block_flags]


class Block(GameObject):
    id = "builtin:none"
    
    drops = []
    
    drawtype = 'image'  # or 'tiled' or None
    drawlayer = 0  # 0 - foreground, 1 - midground, 2 - background
    
    tilecomparable = True  # TODO - find out how to describe this
    
    WIDTH = 16
    HEIGHT = 16

    registered_blocks = {"std:air": {
        "entry": None,
        "id": 0,
    }}

    _registered_blocks = [None]  # int ids for registered entries
                                 # None - air block

    tile = None

    ID = 0
    
    REPLACABLE = False
    
    level = 1  # If tool has too low level, it wouldn't dig this block
    types = None  # Types of tools that can be used to dig this block
                  # None means it can be digged by every item

    def __init__(self, *position):
        pass
    
    @classmethod
    def on_place(cls, x, y):
        '''Called when placed in world'''
        pass
    
    @classmethod
    def on_destroy(cls, x, y):
        pass
    
    # You don't usually need to redefine those methods
    @classmethod
    def _on_destroy(cls, x, y):
        '''Called in World when destroyed'''
        cls.on_destroy(x, y)
        
        entmanager = entitymanager.EntityManager.get()
        
        if entmanager is None:
            print('Warning: could not drop items without EntityManager')
            return
        
        for drop in cls.get_drops():
            ientity, _ = entmanager.newentity('builtin:item_entity', None,
                                           position=(x*cls.WIDTH, y*cls.HEIGHT))
            
            ientity.set_item_stack(drop)

    @classmethod
    def get_drops(cls):
        '''Called in default on_destroy function. Should return
        list of ItemStacks'''
        drops = []
        
        for drop in cls.drops:
            if isinstance(drop, itemstack.ItemStack):
                drops.append(drop.copy())
            elif isinstance(drop, str):
                drops.append(itemstack.ItemStack.from_str(drop))
        
        return drops
    
    @classmethod
    def gettile(cls, x, y):
        '''Get block drawable'''
        if cls.drawtype == 'tiled':
            cls.tile.select(*get_tilemap_position(x, y, cls.drawlayer))
        return cls.tile.get()


    # Blocks definitions storage methods
    # TODO - spit this class into Block and BlockDefStorage
    @classmethod
    def by_id(cls, id):
        '''Get block definition by integer id'''
        try:
            return cls._registered_blocks[id]
        except IndexError:
            pass

    @classmethod
    def by_strid(cls, strid):
        '''Get block definition by string id'''
        block = cls.registered_blocks.get(idstr)
        if block is not None:
            return block["entry"]

    @classmethod
    def id_by_strid(cls, strid):
        '''Get integer block id by string id'''
        return cls.registered_blocks[strid]["id"]

    @classmethod
    def register(cls):
        '''Add block definition into registration table'''
        cls.registered_blocks[cls.id] = {
            "entry": cls,
            "id": -1,
        }

    @classmethod
    def registered_count(cls):
        '''Get count of registered blocks'''
        return len(cls._registered_blocks)

    @classmethod
    def sort_registered_entries(cls):
        '''Initialize integer identifiers for registered blocks'''
        cls._registered_blocks = [None]  # None - std:air

        keys = list(cls.registered_blocks.keys())
        keys.sort()

        for i in range(1, len(keys)):
            cls._registered_blocks.append(cls.registered_blocks[keys[i]]["entry"])
            cls.registered_blocks[keys[i]]['id'] = i
            cls._registered_blocks[i].ID = i


# ---------------------------------------------------------------
# TODO - make this functions better


def _place_block_into(blockname, into=0, consume=True, force=False):  # 0 - fg, 1 - mg, 2 - bg
    def _place_block(player, itemstack, position):
        world = player.world
        
        position = int(position[0]), int(position[1])

        if into == 0:
            dstblock = world.get_fg_block(*position)
        elif into == 1:
            dstblock = world.get_mg_block(*position)
        else:
            dstblock = world.get_bg_block(*position)

        if force or dstblock is None or dstblock.REPLACABLE:
            if into == 0:
                world.set_fg_block(*position, Block.id_by_strid(blockname))
            elif into == 1:
                world.set_mg_block(*position, Block.id_by_strid(blockname))
            else:
                world.set_bg_block(*position, Block.id_by_strid(blockname))
            
            if consume:
                itemstack.consume_items(1)
    
    return _place_block


def _place_block_into_keep(blockname, into=0, consume=True, force=False):  # 0 - fg, 1 - mg, 2 - bg
    _keep_place_block_users = {}
    
    def _place_block_keep(player, itemstack, position, use_time):
        world = player.world

        position = int(position[0]), int(position[1])
        
        if _keep_place_block_users.get(player) is None:
            _keep_place_block_users[player] = 0
        
        if _keep_place_block_users[player] > use_time:
            _keep_place_block_users[player] = use_time
        
        if use_time - _keep_place_block_users[player] > 0.1:
            if into == 0:
                dstblock = world.get_fg_block(*position)
            elif into == 1:
                dstblock = world.get_mg_block(*position)
            else:
                dstblock = world.get_bg_block(*position)

            if force or dstblock is None or dstblock.REPLACABLE:
                if into == 0:
                    world.set_fg_block(*position, Block.id_by_strid(blockname))
                elif into == 1:
                    world.set_mg_block(*position, Block.id_by_strid(blockname))
                else:
                    world.set_bg_block(*position, Block.id_by_strid(blockname))
                
                if consume:
                    itemstack.consume_items(1)
                
                _keep_place_block_users[player] = use_time
    
    return _place_block_keep


def place_fg_block(blockname, consume=True, force=False):
    return _place_block_into(blockname, 0, consume, force)


def place_mg_block(blockname, consume=True, force=False):
    return _place_block_into(blockname, 1, consume, force)


def place_bg_block(blockname, consume=True, force=False):
    return _place_block_into(blockname, 2, consume, force)


def place_fg_block_keep(blockname, consume=True, force=False):
    return _place_block_into_keep(blockname, 0, consume, force)


def place_mg_block_keep(blockname, consume=True, force=False):
    return _place_block_into_keep(blockname, 1, consume, force)


def place_bg_block_keep(blockname, consume=True, force=False):
    return _place_block_into_keep(blockname, 2, consume, force)
