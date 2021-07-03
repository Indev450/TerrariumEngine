import pygame as pg

import game.entity_manager as entitymanager
import game.item_stack as itemstack
import game.world as worldm
import game.block_item as blockitem

from game.texture import gettexture

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


class BlockDefHolder:
    registered_blocks = {}
    registered_blocks_list = []
    
    @classmethod
    def clear(cls):
        cls.registered_blocks = {'builtin:air': None, 'builtin:obstructed': BlockObstructed}
        cls.registered_blocks_list = []
    
    @classmethod
    def by_id(cls, id):
        '''Get block definition by integer id'''
        try:
            return cls.registered_blocks_list[id]
        except IndexError:
            return

    @classmethod
    def by_strid(cls, strid):
        '''Get block definition by string id'''
        return cls.registered_blocks.get(strid)

    @classmethod
    def id_by_strid(cls, strid):
        '''Get integer block id by string id'''
        return cls.registered_blocks[strid].ID

    @classmethod
    def register(cls, block_type):
        '''Add block definition into registration table'''
        cls.registered_blocks[block_type.id] = block_type

    @classmethod
    def registered_count(cls):
        '''Get count of registered blocks'''
        return len(cls.registered_blocks_list)

    @classmethod
    def init_int_ids(cls, preserved=None):
        '''Initialize integer identifiers for registered blocks'''
        cls.registered_blocks_list = [None, BlockObstructed]  # None - std:air
        
        if preserved is not None and preserved:  # If has any values in
            maxid = max(preserved.values())
            
            # Allocate space for preserved blocks
            for i in range(maxid):
                cls.registered_blocks_list.append(None)
        
        elif preserved is None:
            preserved = {}
        
        # Replace all needed slots with block types, even they don't exists.
        # That will help keep map (more or less) not corrupted
        for key in preserved.keys():
            block_type = cls.registered_blocks.get(key)
            
            if block_type is None:
                block_type = make_unknown_block(key)
            
            cls.registered_blocks_list[preserved[key]] = block_type
            block_type.ID = preserved[key]
        
        i = 2  # Skip first 2 entries
        preserved_size = len(cls.registered_blocks_list)  # To avoid IndexError
        registered_keys = iter(cls.registered_blocks.keys())
        
        # Skip:
        next(registered_keys)  # bultin:air
        next(registered_keys)  # bultin:obstructed
        
        while True:
            try:
                if i < preserved_size:
                    if cls.registered_blocks_list[i] is None:
                        # Take a next key. If there is no any, raise StopIteration.
                        # (Actually i though 'while' will handle it, but
                        # looks like i should do it myself)
                        nextkey = next(registered_keys)
                        
                        if preserved.get(nextkey) is not None:
                            # Thats block is already preserved and added to list,
                            # so we can skip it
                            continue

                        cls.registered_blocks_list[i] = cls.registered_blocks[nextkey]
                        cls.registered_blocks_list[i].ID = i
                        
                        preserved[nextkey] = i
                        # Add new block to 'preserved' so next time we
                        # load it block will have same int ID
                    
                    i += 1
                
                else:
                    # Same as above. Used when there is no free slots left
                    nextkey = next(registered_keys)

                    if preserved.get(nextkey) is not None:
                        continue
                    
                    cls.registered_blocks_list.append(cls.registered_blocks[nextkey])
                    
                    cls.registered_blocks_list[i].ID = i
                    
                    preserved[nextkey] = i
                    
                    i += 1
            
            except StopIteration:
                break

        return preserved


class Block:
    """
    # Block definition.
    
    `id` (string, required) - identifier for block
    
    `drawtype` (string, one of 'image', 'tiled', or None) - describes how
    to draw block. 'image' - draw single block image, 'tiled' - draw block
    image based on its neighbours, None - do not draw block
    
    `layer` (integer, 0 - fg, 1 - mg, 2 - bg) - layer number
    
    `tilecomparable` (boolean, used only for drawtype='tiled') - describes
    is this block counts as neighbour for other 'tiled' blocks
    
    `tile` (game.texture.Texture derived object) - texture for block
    
    `drops` (list of ItemStack objects or strings) - items dropped when block
    broken
    
    `replacable` (boolean) - is this block can be replaced
    
    `level` (integer) - minimal tool level required to break this block
    
    `tool_types` (iterable or None) - specific tool types/categories required
    to break this block
    
    `hits` (integer) - how much hits this block requires to broke
    
    `hit_sound` (game.sound.Sound derived object) - sound when player hits block
    
    `register_item` (bool) - add item based on the block. Default - True
    
    `inventory_image` (game.texture.Texture derived object) - texture for block item
    
    # Engine variables (don't change them)
    
    `WIDTH` and `HEIGHT` (integers) - size of block
    
    `ID` (integer) - block id assigned in BlockDefHolder.init_int_ids()
    """
    id = "builtin:none"
    
    drawtype = 'image'
    
    layer = 0
    
    tilecomparable = True

    tile = None
    
    drops = []
    
    replacable = False
    
    level = 1
    
    tool_types = None
    
    hits = 4
    
    hit_sound = None
    
    register_item = True
    
    inventory_image = None
    
    collide_up = collide_down = collide_left = collide_right = True
    
    custom_rect = None
    
    WIDTH = 16
    HEIGHT = 16

    ID = 0
    
    @classmethod
    def on_place(cls, x, y):
        '''Called when placed in world'''
        pass
    
    @classmethod
    def on_destroy(cls, x, y):
        '''Called in Block._on_destroy when block destroyed'''
        pass
    
    @classmethod
    def on_load(cls, x, y):
        '''Called when chunk loads this block'''
        pass
    
    @classmethod
    def _on_destroy(cls, x, y):
        '''Called in World when block destroyed'''
        cls.on_destroy(x, y)
        
        entmanager = entitymanager.EntityManager.get()
        
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
            cls.tile.select(*get_tilemap_position(x, y, cls.layer))
        return cls.tile.get()
    
    @classmethod
    def register(cls):
        BlockDefHolder.register(cls)
        
        if cls.register_item:
            blockitem.register_block_item(cls)


class BlockObstructed(Block):
    id = 'builtin:obstructed'
    ID = 1


def make_unknown_block(id):
    """Creates new UnknownBlock type to not mix other unknown blocks"""
    class UnknownBlock(Block):
        id = id
        
        drops = [id]
        
        tile = gettexture('resources/textures/blocks/unknown_block.png')
    
    return UnknownBlock

# ---------------------------------------------------------------
# TODO - make this functions better


def _block_position(x, y):
    return int(x // Block.WIDTH), int(y // Block.HEIGHT)


def _place_block(blockname, layer=0, consume=True, force=False):  # 0 - fg, 1 - mg, 2 - bg
    from utils.items import do_cooldown  # Circular imports!
    cooldown = do_cooldown(0.1)
    
    def _place_block(player, itemstack, position):
        if not cooldown(player):
            return

        world = player.world
        
        position = _block_position(*position)
        
        if layer == 0:
            rect = pg.Rect(
                position[0]*Block.WIDTH, position[1]*Block.HEIGHT,
                Block.WIDTH, Block.HEIGHT)
            
            if player.rect.colliderect(rect):
                return

        dstblock = world.get_block(*position, layer)

        if force or dstblock is None or dstblock.replacable:
            world.set_block(*position, layer, BlockDefHolder.id_by_strid(blockname))
            
            if consume:
                itemstack.consume_items(1)
    
    return _place_block


def _place_block_keep(blockname, layer=0, consume=True, force=False):
    from utils.items import do_cooldown  # Circular imports!
    cooldown = do_cooldown(0.1)
    
    def _place_block_keep(player, itemstack, position, use_time):
        if not cooldown(player):
            return

        world = player.world

        position = _block_position(*position)
        
        if layer == 0:
            rect = pg.Rect(
                position[0]*Block.WIDTH, position[1]*Block.HEIGHT,
                Block.WIDTH, Block.HEIGHT)
            
            if player.rect.colliderect(rect):
                return

        dstblock = world.get_block(*position, layer)

        if force or dstblock is None or dstblock.replacable:
            world.set_block(*position, layer, BlockDefHolder.id_by_strid(blockname))
            
            if consume:
                itemstack.consume_items(1)
    
    return _place_block_keep


def place_fg_block(blockname, consume=True, force=False):
    return _place_block(blockname, 0, consume, force)


def place_mg_block(blockname, consume=True, force=False):
    return _place_block(blockname, 1, consume, force)


def place_bg_block(blockname, consume=True, force=False):
    return _place_block(blockname, 2, consume, force)


def place_fg_block_keep(blockname, consume=True, force=False):
    return _place_block_keep(blockname, 0, consume, force)


def place_mg_block_keep(blockname, consume=True, force=False):
    return _place_block_keep(blockname, 1, consume, force)


def place_bg_block_keep(blockname, consume=True, force=False):
    return _place_block_keep(blockname, 2, consume, force)
