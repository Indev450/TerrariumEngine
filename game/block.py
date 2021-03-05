import pygame as pg

from .game_object import GameObject

import game.entity_manager as entitymanager
import game.item_stack as itemstack
import game.world as worldm

from tilemap.maketilemap import tilemap_positions, flags


def get_tilemap_position(x, y, layer):
    world = worldm.World.get()
    
    getblock = (world.get_fg_block if layer == 0 else
                world.get_mg_block if layer == 1 else
                world.get_bg_block if layer == 2 else lambda: 0)
    
    block_flags = 0
    
    up = getblock(x, y-1)
    down = getblock(x, y+1)
    left = getblock(x-1, y)
    right = getblock(x+1, y)
    
    block_flags |= flags['up'] if up is None or not up.tilecomparable else 0
    block_flags |= flags['down'] if down is None or not down.tilecomparable else 0
    block_flags |= flags['left'] if left is None or not left.tilecomparable else 0
    block_flags |= flags['right'] if right is None or not right.tilecomparable else 0
    
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
        super().__init__(*position, self.WIDTH, self.HEIGHT)

        self.image = self.tile

        self.grid_x = position[0] // self.WIDTH
        self.grid_y = position[1] // self.HEIGHT

    def getid(self):
        return self.ID
    
    def on_destroy(self):
        entmanager = entitymanager.EntityManager.get()
        
        if entmanager is None:
            print('Warning: could not drop items without EntityManager')
            return
        
        for drop in self.get_drops():
            ientity, _ = entmanager.newentity('builtin:item_entity', None,
                                           position=self.rect.topleft)
            
            ientity.set_item_stack(drop)
    
    def on_place(self, x, y):
        """Called when placed in world"""
        pass
    
    def get_drops(self):
        '''Called in default on_destroy function. Should return
        list of ItemStacks'''
        drops = []
        
        for drop in self.drops:
            if isinstance(drop, itemstack.ItemStack):
                drops.append(drop.copy())
            elif isinstance(drop, str):
                drops.append(itemstack.ItemStack.from_str(drop))
        
        return drops
    
    def gettile(self):
        if self.drawtype == 'tiled':
            self.image.select(*get_tilemap_position(self.grid_x, self.grid_y, self.drawlayer))
        return self.image.get()

    @classmethod
    def by_id(cls, id):
        try:
            return cls._registered_blocks[id]
        except IndexError:
            pass

    @classmethod
    def id_by_strid(cls, strid):
        return cls.registered_blocks[strid]["id"]

    @classmethod
    def by_idstr(cls, idstr):
        block = cls.registered_blocks.get(idstr)
        if block is not None:
            return block["entry"]

    @classmethod
    def register(cls):
        cls.registered_blocks[cls.id] = {
            "entry": cls,
            "id": -1,
        }

    @classmethod
    def registered_count(cls):
        return len(cls._registered_blocks)

    @classmethod
    def sort_registered_entries(cls):
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
