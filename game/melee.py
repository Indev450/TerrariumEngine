import time

from pygame.math import Vector2

from utils.items import do_cooldown

from .entity import Entity
from .entity_manager import EntityManager


class Swing(Entity):
    SIZE = (16, 16)
    
    OFFSET = (0, 0)  # Offset from parent.center
    
    TTL = 0.5
    
    DAMAGE = 0
    
    TARGET_TAGS = ["hittable"]

    def __init__(self, parent,
                 facing_left=True,
                 manager=None,
                 uuid=None):
        super().__init__(
            manager=manager,
            uuid=uuid,
            size=self.SIZE)
        
        self.parent = parent
        
        self.offset = Vector2(self.OFFSET)
        
        if facing_left:
            self.offset.x *= -1
        
        self.ttl = self.TTL
        
        self.entities_hit = set()
        self.entities_hit.add(parent)  # Don't hit parent entity
    
    def update(self, dtime):
        self.ttl -= dtime
        
        if self.ttl <= 0:
            self.manager.delentity(self.uuid)
            return
        
        self.rect.center = self.parent.rect.center
        
        self.rect.center += self.offset
        
        for tag in self.TARGET_TAGS:
            for entity in self.manager.get_tagged_entities(tag):
                if entity.rect.colliderect(self.rect) and entity not in self.entities_hit:
                    self.entities_hit.add(entity)
                    entity.hurt(self.DAMAGE)


def do_swing(swing_id, speed):
    cooldown = do_cooldown(1.0 / speed)
    
    def inner_do_swing(player, itemstack, position):
        if cooldown(player):
            manager = EntityManager.get()
            
            manager.newentity(swing_id, None, parent=player, facing_left=player.turned_left)
    
    return inner_do_swing


def do_swing_keep(swing_id, speed):
    cooldown = do_cooldown(1.0 / speed)
    
    def inner_do_swing_keep(player, itemstack, position, use_time):
        if cooldown(player):
            manager = EntityManager.get()
            
            manager.newentity(swing_id, None, parent=player, facing_left=player.turned_left)
    
    return inner_do_swing_keep
