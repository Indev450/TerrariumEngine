from game.block import Block
from game.world import World
from pygame.math import Vector2


def do_break_block(radius, layer=0):
    def inner_break_block(player, itemstack, position):
        playerpos = player.rect.center[0] // Block.WIDTH, player.rect.center[1] // Block.HEIGHT
        
        if Vector2(playerpos).distance_to(Vector2(position)) > radius:
            return
        
        position = int(position[0]), int(position[1])
        
        tool_level = getattr(itemstack.item_t, 'level', 1)
        tool_dig_type = getattr(itemstack.item_t, 'dig_type', None)
        
        _try_break_block(*position, tool_level, tool_dig_type, layer)
    
    return inner_break_block


def do_break_block_keep(radius, speed, layer=0):
    players_use_time = {}
    cooldown = 1.0 / speed
    
    def inner_break_block_keep(player, itemstack, position, use_time):
        playerpos = player.rect.center[0] // Block.WIDTH, player.rect.center[1] // Block.HEIGHT
        
        if Vector2(playerpos).distance_to(Vector2(position)) > radius:
            return

        world = player.world
        
        position = int(position[0]), int(position[1])
        
        if players_use_time.get(player) is None:
            players_use_time[player] = 0
        
        if players_use_time[player] > use_time:
            players_use_time[player] = use_time
        
        if use_time - players_use_time[player] > cooldown:
            tool_level = getattr(itemstack.item_t, 'level', 1)
            tool_dig_type = getattr(itemstack.item_t, 'dig_type', None)
            
            _try_break_block(*position, tool_level, tool_dig_type, layer)
            
            players_use_time[player] = use_time
    
    return inner_break_block_keep


def _try_break_block(x, y, tool_level, tool_dig_type, layer=0):
    world = World.get()
    
    block = world.get_block(x, y, layer)
    
    if block is None:
        return
    
    if block.level is not None and tool_level < block.level:
        return
    
    if block.types is not None and tool_dig_type is not None:
        for btype in block.types:
            if btype == tool_dig_type:
                break
        else:
            return
    
    world.set_block(x, y, layer, 0)
