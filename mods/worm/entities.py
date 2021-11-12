from game.texture import gettexture, gettiled, animtiled
from game.sound import getsound
from game.hittable_entity import HittableEntity
from game.entity_manager import EntityManager
from game.entity import Entity
from game.world import World
from game.block import Block

from mods.manager import modpath

from utils.entities import Spawner


def do_death_particles(entmgr, position, srcvelocity):
    for i in range(20):
        entmgr.newentity('worm:particle_metal', None, position=position,
                                                      srcvelocity=srcvelocity)
    
    entmgr.newentity('worm:particle_smoke', None, position=position)


class WormHead(HittableEntity):
    ID = 'worm:worm_head'
    
    TEXTURE = gettiled(modpath('textures/entities/worm_head.png'), 2, 1)
    
    ANIMSPEC = {
        'main': {
            'speed': 1.0/4,
            'tiles': [(0, 0), (1, 0)],
        }
    }
    
    SND_CRUMBLE = getsound(modpath('sounds/crumble.wav'))
    SND_DEATH = getsound(modpath('sounds/explosion.wav'))
    SND_HURT = getsound(modpath('sounds/hurt.wav'))
    
    XACC = 15
    YACC = 12
    
    HP_MAX = 100
    
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
        
        self.ignore_collision = True
        
        self.child, _ = manager.newentity(WormBody.ID, None,
                                          position=position,
                                          parent=self,
                                          segmentno=self.SEGCOUNT)
        
        self.in_ground = True
        
        self.add_tag('hittable')
        
    def update(self, dtime):
        self.child.move_to_parent()
        
        super().update(dtime)
        
        bx, by = self.rect.centerx // Block.WIDTH, self.rect.centery // Block.HEIGHT
        
        player = self.manager.get_tagged_entities('player')[0]
        
        if self.rect.colliderect(player.rect):
            player.hurt(5, entity=self, inv_time=1)
        
        if self.world.get_fg_block(bx, by) is None:
            if self.in_ground:
                self.SND_CRUMBLE.play_at(self.rect.center)
                
                self.in_ground = False
                self.friction = 20
        
        else:
            if not self.in_ground:
                self.SND_CRUMBLE.play_at(self.rect.center)
                
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
    
    def on_death(self, entity=None):
        self.child.on_death()
        
        do_death_particles(self.manager, self.rect.center, (self.xv, self.yv))
        
        self.manager.delentity(self.uuid)
    
    def do_knockback(self, knockback, entity=None):
        pass  # Ignore knockback


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
        
        self.add_tag('hittable')
    
    def update(self, dtime):
        player = self.manager.get_tagged_entities('player')[0]
        
        if self.rect.colliderect(player.rect):
            player.hurt(5, entity=self, inv_time=1)
    
    def move_to_parent(self):
        distx = self.rect.centerx - self.parent.rect.centerx
        disty = self.rect.centery - self.parent.rect.centery
        dist = (distx*distx + disty*disty)**0.5
        
        if dist != 0:
            if self.child is not None:
                self.child.move_to_parent()
            
            self.xv, self.yv = distx * (dist-self.MINDIST)/dist, disty * (dist-self.MINDIST)/dist
            
            self.rect.centerx -= self.xv
            self.rect.centery -= self.yv
    
    def on_death(self):
        if self.child is not None:
            self.child.on_death()
        
        do_death_particles(self.manager, self.rect.center, (-self.xv, -self.yv))
        # For some reason speed is negative
        
        self.manager.delentity(self.uuid)
    
    def hurt(self, damage, entity=None, knockback=0, inv_time=0):
        self.parent.hurt(damage)


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
