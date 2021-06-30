import math

import pygame as pg

from pygame.math import Vector2

from .entity import Entity
from .entity_manager import EntityManager
from .block import Block

from .texture import gettransparent


class TreeDef:
    ID = 'builtin:tree'

    TEXTURE = None
    SND_CHOP = None
    SND_CHOPPED = None

    SIZE = (64, 128)

    # Hitbox used for chopping the tree. Not using default rect to be hittable
    # only at trunk.
    HITBOX_SIZE = (16, 96)
    HITBOX_OFFSET = (24, 32)
    
    HP = 8  # Number of hits required to chop the tree
    
    drops = []  # Same as Block.drops
    
    SHAKE_AMPLITUDE = 8  # For shake effect
    
    @classmethod
    def register(cls):
        register_tree(cls)


def register_tree(cls):
    class TreeEntity(Entity):
        ID = f'{cls.ID}_entity'
        
        def __init__(self,
                     manager=None,
                     uuid=None,
                     position=(0, 0)):
            super().__init__(manager=manager,
                             uuid=uuid,
                             position=(position[0] - cls.SIZE[0]//2,
                                       position[1] + Block.HEIGHT - cls.SIZE[1]),
                             velocity=(0, 0),
                             size=cls.SIZE)
            
            self.hp = self.max_hp = cls.HP
            
            self.dec_max_hp_time = 0  # Will decrease max_hp to hp each half second
                                      # while not hit to fix endless shaking of tree
            
            self.image = cls.TEXTURE
            
            self.shake_offset = 0
            self.shake_time = 0
            
            self.add_tag('choppy')
            
            self.chop_rect = pg.Rect(
                (self.rect.x + cls.HITBOX_OFFSET[0],
                 self.rect.y + cls.HITBOX_OFFSET[1]),
                cls.HITBOX_SIZE)
            
            y = position[1] // Block.HEIGHT
            
            self.block = (position[0] // Block.WIDTH, position[1] // Block.HEIGHT)
            self.check_blocks = [(x//Block.WIDTH, y+1) for x in range(self.chop_rect.x, self.chop_rect.x+self.chop_rect.width, Block.WIDTH)]
        
        def update(self, dtime):
            for block in self.check_blocks:
                if self.world.get_fg_block(*block) is None:
                    self.on_chopped()
                    return
            
            if self.max_hp > self.hp:
                self.dec_max_hp_time += dtime
                
                if self.dec_max_hp_time >= 0.5:
                    self.max_hp -= 1
                    
                    self.dec_max_hp_time = 0
            
            self.shake_time += dtime
            
            # 2*3.14*(cls.HP - self.hp) - Angular frequency (2*pi*v)
            self.shake_offset = int(cls.SHAKE_AMPLITUDE * math.sin(2*3.14*(self.max_hp - self.hp)*self.shake_time) * (self.max_hp - self.hp) / self.max_hp)
        
        def chop(self, damage=1):
            self.hp -= damage
            
            if self.hp <= 0:
                self.on_chopped()
            
            else:
                if cls.SND_CHOP is not None:
                    cls.SND_CHOP.play()
                
                self.max_hp = cls.HP

        def on_chopped(self):
            self.world.set_mg_block(*self.block, 0)
            
            if cls.SND_CHOPPED is not None:
                cls.SND_CHOPPED.play()
        
        def draw(self, screen):
            self.rect.x += self.shake_offset
            
            super().draw(screen)
            
            self.rect.x -= self.shake_offset
    
    class TreeBlock(Block):
        id = cls.ID
        
        loaded = {}
        
        _entmgr = None
        
        drops = cls.drops
        
        tile = gettransparent(1, 1)
        
        @classmethod
        def on_load(cls, x, y):
            super().on_load(x, y)
            
            cls.add_block_entity(x, y)
        
        @classmethod
        def on_place(cls, x, y):
            super().on_place(x, y)
            
            cls.add_block_entity(x, y)
        
        @classmethod
        def on_destroy(cls, x, y):
            super().on_destroy(x, y)
            
            manager = EntityManager.get()
            
            if cls._entmgr is not manager:
                cls._entmgr = manager
                cls.loaded = {}
            
            uuid = cls.loaded.get((x, y))
            
            if uuid is not None:
                manager.delentity(uuid)
        
        @classmethod
        def add_block_entity(cls, x, y):
            manager = EntityManager.get()
            
            if cls._entmgr is not manager:
                cls._entmgr = manager
                cls.loaded = {}
            
            if cls.loaded.get((x, y)) is None:
                _, cls.loaded[(x, y)] = manager.newentity(
                    f'{cls.id}_entity', None,
                    position=(Block.WIDTH*x, Block.HEIGHT*y))
        
        def mg_can_place(mapgen, x, y):
            check_blocks = [mapgen.get_foreground(_x, y+1) != 0 for _x in range(x-cls.SIZE[0]//Block.WIDTH//2, x+cls.SIZE[0]//Block.WIDTH//2)]
            check_no_blocks = [mapgen.get_foreground(_x, y) == 0 for _x in range(x-cls.SIZE[0]//Block.WIDTH//2, x+cls.SIZE[0]//Block.WIDTH//2)]
            
            return all(check_blocks) and all(check_no_blocks) and mapgen.get_foreground(x, y) == 0
        
        def can_place(world, x, y):
            check_blocks = [world.get_fg_block(_x, y+1) is not None for _x in range(x-cls.SIZE[0]//Block.WIDTH//2, x+cls.SIZE[0]//Block.WIDTH//2)]
            check_no_blocks = [world.get_fg_block(_x, y) is None for _x in range(x-cls.SIZE[0]//Block.WIDTH//2, x+cls.SIZE[0]//Block.WIDTH//2)]
            
            return all(check_blocks) and all(check_no_blocks) and world.get_fg_block(x, y) is None
    
    TreeEntity.register()
    TreeBlock.register()


def do_chop_tree(radius, damage=1):
    def inner_chop_tree(player, itemstack, position):
        if Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH:
            return
        
        manager = EntityManager.get()
        
        for entity in manager.get_tagged_entities('choppy'):
            if entity.chop_rect.collidepoint(position):
                entity.chop(damage)
    
    return inner_chop_tree


def do_chop_tree_keep(radius, speed, damage=1):
    players_use_time = {}
    cooldown = 1.0 / speed
    
    def inner_chop_tree_keep(player, itemstack, position, use_time):
        if Vector2(player.rect.center).distance_to(Vector2(position)) > radius * Block.WIDTH:
            return
        
        if players_use_time.get(player) is None:
            players_use_time[player] = 0
        
        if players_use_time[player] > use_time:
            players_use_time[player] = use_time
        
        if use_time - players_use_time[player] > cooldown:
            manager = EntityManager.get()
            
            for entity in manager.get_tagged_entities('choppy'):
                if entity.chop_rect.collidepoint(position):
                    entity.chop(damage)
            
            players_use_time[player] = use_time
    
    return inner_chop_tree_keep
