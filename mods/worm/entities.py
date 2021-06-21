from math import sin, cos, radians, degrees

from pygame.math import Vector2 as vec

from game.texture import gettexture, gettiled, animtiled
from game.sound import getsound
from game.entity import Entity
from game.entity_manager import EntityManager
from game.world import World
from game.block import Block

from mods.manager import modpath

from utils.entities import Spawner


class WormHead(Entity):
    ID = 'worm:worm_head'
    
    TEXTURE = gettiled(modpath('textures/entities/worm_head.png'), 2, 1)
    
    ANIMSPEC = {
        'main': {
            'speed': 1.0/4,
            'tiles': [(0, 0), (1, 0)],
        }
    }
    
    SND_CRUMBLE = getsound(modpath('sounds/crumble.wav'))
    
    XACC = 15
    YACC = 12
    
    MAX_SPEED = 4
    
    GRAVITY = 5
    
    HITTIME = 0.6
    
    SEGCOUNT = 12
    
    BRAKING = 1
    
    def __init__(self,
                 manager=None,
                 uuid=None,
                 position=(0, 0)):
        super().__init__(manager=manager,
                         uuid=uuid,
                         position=position,
                         velocity=(0, 0),
                         size=(32, 32))
        
        self.image = animtiled(self.TEXTURE, self.ANIMSPEC, 'main')
        
        player = manager.get_tagged_entities('player')[0]
        
        #self.rect.center = player.rect.center
        
        self.ignore_collision = True
        
        self.child, _ = manager.newentity(WormBody.ID, None,
                                          position=position,
                                          parent=self,
                                          segmentno=self.SEGCOUNT)
        
        self.in_ground = True
        
    def update(self, dtime):
        self.child.move_to_parent()
        
        super().update(dtime)
        
        bx, by = self.rect.centerx // Block.WIDTH, self.rect.centery // Block.HEIGHT
        
        player = self.manager.get_tagged_entities('player')[0]
        
        if self.rect.colliderect(player.rect):
            player.hurt(5, self)
        
        if self.world.get_fg_block(bx, by) is None:
            if self.in_ground:
                distx = self.rect.centerx - player.rect.centerx
                disty = self.rect.centery - player.rect.centery
                dist = (distx*distx + disty*disty)**0.5
                
                volume = min(Block.WIDTH*6/dist, 1.0)
                
                if volume > 0.1:
                    self.SND_CRUMBLE.sound.set_volume(volume)
                    self.SND_CRUMBLE.play(0)
                
                self.in_ground = False
                self.friction = 20
        
        else:
            if not self.in_ground:
                distx = self.rect.centerx - player.rect.centerx
                disty = self.rect.centery - player.rect.centery
                dist = (distx*distx + disty*disty)**0.5
                
                volume = min(Block.WIDTH*6/dist, 1.0)
                
                if volume > 0.1:
                    self.SND_CRUMBLE.sound.set_volume(volume)
                    self.SND_CRUMBLE.play(0)
                
                self.in_ground = True
            
            if self.rect.centerx > player.rect.centerx:
                if self.xv > -self.MAX_SPEED:
                    self.xv -= self.XACC * dtime
            else:
                if self.xv < self.MAX_SPEED:
                    self.xv += self.XACC * dtime
            
            if self.rect.centery > player.rect.centery:
                if self.yv > -self.MAX_SPEED:
                    self.yv -= self.YACC * dtime
            else:
                if self.yv < self.MAX_SPEED:
                    self.yv += self.YACC * dtime


class WormBody(Entity):
    ID = 'worm:worm_body'
    
    HITTIME = 0.6
    
    MINDIST = Block.WIDTH
    
    TEXTURE = gettexture(modpath('textures/entities/worm_body.png'))
    
    def __init__(self,
                 manager=None,
                 uuid=None,
                 position=(0, 0),
                 parent=None,
                 segmentno=0):
        super().__init__(manager=manager,
                         uuid=uuid,
                         position=position,
                         velocity=(0, 0),
                         size=(32, 32))
        
        self.image = self.TEXTURE
        
        self.parent = parent
        
        self.child = None
        
        if segmentno > 0:
            self.child, _ = manager.newentity(self.ID, None,
                                              position=position,
                                              parent=self,
                                              segmentno=segmentno-1)
    
    def update(self, dtime):
        player = self.manager.get_tagged_entities('player')[0]
        
        if self.rect.colliderect(player.rect):
            player.hurt(5, self)
    
    def move_to_parent(self):
        distx = self.rect.centerx - self.parent.rect.centerx
        disty = self.rect.centery - self.parent.rect.centery
        dist = (distx*distx + disty*disty)**0.5
        
        if dist != 0:
            if self.child is not None:
                self.child.move_to_parent()
            
            self.rect.centerx -= distx * (dist-self.MINDIST)/dist
            self.rect.centery -= disty * (dist-self.MINDIST)/dist


class WormSpawner(Spawner):
    MAXENTITIES = 1

    def can_spawn(self, x, y):
        world = World.get()
        
        if world is None:
            return False
        
        x, y = x//Block.WIDTH, y//Block.HEIGHT
        
        return world.get_fg_block(x, y) is not None and world.within_bounds(x, y)
    
    def spawn(self, entmanager, x, y):
        _, key = entmanager.newentity(WormHead.ID, None, position=(x, y))
        
        return key
