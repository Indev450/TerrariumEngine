from game.block import Block
from game.world import World
from pygame.math import Vector2


def break_block(radius, layer=0):
    def decor_break_block(player, itemstack, position):
        if Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH:
            return
        
        position = int(position[0]), int(position[1])
        
        tool_level = getattr(itemstack.item_t, 'level', 1)
        tool_dig_type = getattr(itemstack.item_t, 'dig_type', None)
        
        try_break_block(*position, tool_level, tool_dig_type, layer)
    
    return decor_break_block


def try_break_block(x, y, tool_level, tool_dig_type, layer=0):
    world = World.get()
    
    block = world.get_block_layer(x, y, layer)
    
    if block.level is not None and tool_level < block.level:
        return
    
    if block.TYPES is not None:
        for btype in block.types:
            if btype == tool_dig_type:
                break
        else:
            return
    
    world.set_block_layer(x, y, layer, 0)
