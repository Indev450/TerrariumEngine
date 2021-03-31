import weakref

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
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance
    
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


def do_break_block(radius, layer=0):
    def inner_break_block(player, itemstack, position):
        if Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH:
            return
        
        position = int(position[0]//Block.WIDTH), int(position[1]//Block.HEIGHT)
        
        _try_break_block(*position, itemstack.item_t, layer)
    
    return inner_break_block


def do_break_block_keep(radius, speed, layer=0):
    players_use_time = {}
    cooldown = 1.0 / speed
    
    def inner_break_block_keep(player, itemstack, position, use_time):
        if Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH:
            return

        world = player.world
        
        position = int(position[0]//Block.WIDTH), int(position[1]//Block.HEIGHT)
        
        if players_use_time.get(player) is None:
            players_use_time[player] = 0
        
        if players_use_time[player] > use_time:
            players_use_time[player] = use_time
        
        if use_time - players_use_time[player] > cooldown:
            _try_break_block(*position, itemstack.item_t, layer)
            
            players_use_time[player] = use_time
    
    return inner_break_block_keep


def do_break_blocks(radius, break_radius=1, layer=0):
    def inner_break_blocks(player, itemstack, position):
        if Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH:
            return
        
        _x, _y = position[0]/Block.WIDTH + 0.5, position[1]/Block.HEIGHT + 0.5
        
        for x in range(int(_x-break_radius), int(_x+break_radius)):
            for y in range(int(_y-break_radius), int(_y+break_radius)):
                _try_break_block(x, y, itemstack.item_t, layer)
    
    return inner_break_blocks


def do_break_blocks_keep(radius, speed, break_radius=1, layer=0):
    players_use_time = {}
    cooldown = 1.0 / speed
    
    def inner_break_blocks_keep(player, itemstack, position, use_time):
        if Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH:
            return

        world = player.world
        
        _x, _y = position[0]/Block.WIDTH + 0.5, position[1]/Block.HEIGHT + 0.5
        
        if players_use_time.get(player) is None:
            players_use_time[player] = 0
        
        if players_use_time[player] > use_time:
            players_use_time[player] = use_time
        
        if use_time - players_use_time[player] > cooldown:
            for x in range(int(_x-break_radius), int(_x+break_radius)):
                for y in range(int(_y-break_radius), int(_y+break_radius)):
                    _try_break_block(x, y, itemstack.item_t, layer)
            
            players_use_time[player] = use_time
    
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
