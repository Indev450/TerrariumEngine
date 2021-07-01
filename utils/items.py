import weakref
import time

from game.decorations import Decor, DecorationManager
from game.texture import gettiled
from game.block import Block
from game.world import World
from pygame.math import Vector2


class BlockDamageDecor(Decor):
    texture = gettiled('resources/textures/blocks/breaking.png', 3, 1)
    
    max_lifetime = 5.0
    
    def __init__(self, manager, x, y):
        super().__init__(manager, x, y)
        
        self.damage = 0
    
    def set_damage(self, damage):
        self.damage = damage
    
    def draw(self, screen):
        self.image.select(x=self.damage)
        
        super().draw(screen)


class BlockDamager:
    instance = None
    
    @classmethod
    def get(cls):
        # Probably not the best solution
        try:
            return World.get()._blockdamager
        except AttributeError:
            damager = World.get()._blockdamager = BlockDamager()
            return damager
    
    def __init__(self):
        self.blocks = {}
        self.decormanager = DecorationManager.get()
        self.world = World.get()
    
    def decor_damage(self, x, y):
        decor = BlockDamageDecor(self.decormanager,
                                x*Block.WIDTH, y*Block.HEIGHT)
        decor.image.select(x=0)
        self.decormanager.add(decor)
        
        return weakref.ref(decor)
        
    def damage(self, x, y, layer, damage=1):
        if self.blocks.get((x, y, layer)) is None or self.blocks[(x, y, layer)]['decor']() is None:
            self.blocks[(x, y, layer)] = {
                'damage': 1,
                'required_damage': self.world.get_block(x, y, layer).hits,
                'decor': self.decor_damage(x, y)
            }
        else:
            block = self.blocks[(x, y, layer)]
            
            block['damage'] += damage
            
            damage_percent = block['damage'] / block['required_damage']
            
            if damage_percent < 0.33:
                block['decor']().set_damage(0)
            
            if 0.33 <= damage_percent < 0.66:
                block['decor']().set_damage(1)
            
            if 0.66 <= damage_percent < 1:
                block['decor']().set_damage(2)

            if damage_percent >= 1:
                self.world.set_block(x, y, layer, 0)
                
                self.decormanager.remove(block['decor']())
                del self.blocks[(x, y, layer)]


def do_break_block(radius, speed, layer=0):
    cooldown = do_cooldown(1.0 / speed)
    
    def inner_break_block(player, itemstack, position):
        if (Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH
            or not cooldown(player)):
            return
        
        position = int(position[0]//Block.WIDTH), int(position[1]//Block.HEIGHT)
        
        _try_break_block(*position, itemstack.item_t, layer)
    
    return inner_break_block


def do_break_block_keep(radius, speed, layer=0):
    cooldown = do_cooldown(1.0 / speed)
    
    def inner_break_block_keep(player, itemstack, position, use_time):
        if (Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH
            or not cooldown(player)):
            return
        
        position = int(position[0]//Block.WIDTH), int(position[1]//Block.HEIGHT)
        
        _try_break_block(*position, itemstack.item_t, layer)
    
    return inner_break_block_keep


def do_break_blocks(radius, speed, break_radius=1, layer=0):
    cooldown = do_cooldown(1.0 / speed)
    
    def inner_break_blocks(player, itemstack, position):
        if (Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH
            or not cooldown(player)):
            return
        
        _x, _y = position[0]/Block.WIDTH + 0.5, position[1]/Block.HEIGHT + 0.5
        
        for x in range(int(_x-break_radius), int(_x+break_radius)):
            for y in range(int(_y-break_radius), int(_y+break_radius)):
                _try_break_block(x, y, itemstack.item_t, layer)
    
    return inner_break_blocks


def do_break_blocks_keep(radius, speed, break_radius=1, layer=0):
    cooldown = do_cooldown(1.0 / speed)
    
    def inner_break_blocks_keep(player, itemstack, position, use_time):
        if (Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH
            or not cooldown(player)):
            return
        
        _x, _y = position[0]/Block.WIDTH + 0.5, position[1]/Block.HEIGHT + 0.5
        
        for x in range(int(_x-break_radius), int(_x+break_radius)):
            for y in range(int(_y-break_radius), int(_y+break_radius)):
                _try_break_block(x, y, itemstack.item_t, layer)
    
    return inner_break_blocks_keep


def _try_break_block(x, y, tool, layer=0):
    tool_level = getattr(tool, 'level', 1)
    tool_dig_type = getattr(tool, 'dig_type', None)
    tool_damage = getattr(tool, 'dig_damage', 1)
    
    world = World.get()
    
    block = world.get_block(x, y, layer)
    
    if block is None:
        return
    
    if block.level is not None and tool_level < block.level:
        return
    
    if block.tool_types is not None and tool_dig_type is not None:
        for tool_type in block.tool_types:
            if tool_type == tool_dig_type:
                break
        else:
            return
    
    if block.hit_sound is not None:
        block.hit_sound.play()
    
    block_damager = BlockDamager.get()
    
    block_damager.damage(x, y, layer, tool_damage)


def do_cooldown(cooldown):
    """Returns function, that takes one argument - actor (player for example)
    Every call function checks if there was enough time since last _action_.
    If time since last _action_ is greatter than _cooldown_, it returns True and
    sets new _action_ time. Otherwise, returns False
    
    Example:
    
    def do_stuff(args):
        cooldown = do_cooldown(<cooldown>)
        
        def inner_do_stuff(player, itemstack, position):
            if <some exit conditions> or not cooldown(player):
                return
            ...
        
        return inner_do_stuff
    """
    last_use = {}
    
    def inner_do_cooldown(actor):
        if last_use.get(actor) is None:
            last_use[actor] = 0
        
        if time.time() - last_use[actor] > cooldown:
            last_use[actor] = time.time()
            
            return True
        
        return False
    
    return inner_do_cooldown
