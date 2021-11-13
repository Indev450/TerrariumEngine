from random import uniform, randint

from pygame.math import Vector2

from game.entity import Entity

from game.block import Block

from game.texture import gettiled

from mods.manager import modpath


class WormParticleMetal(Entity):
    ID = 'worm:particle_metal'
    
    TEXTURE = gettiled(modpath('textures/particles/metal.png'), 4, 1)
    
    GRAVITY = 6.5
    
    BRAKING = 1
    
    TTL = 8
    
    def __init__(self,
                 manager=None,
                 uuid=None,
                 position=(0, 0),
                 srcvelocity=(0, 0)):
        super().__init__(
            manager=manager,
            uuid=uuid,
            position=position,
            velocity=(srcvelocity[0] + uniform(-2, 2),
                      srcvelocity[1] + uniform(-3, 1)))
        
        self.frameno = randint(0, 3)
        
        self.ignore_collision = self.world.get_fg_block(int(position[0]/Block.WIDTH), int(position[1]/Block.HEIGHT)) is not None
        
        self.image = self.TEXTURE
        
        self.lifetime = self.TTL
    
    def update(self, dtime):
        super().update(dtime)
        
        self.lifetime -= dtime
        
        if self.lifetime <= 0:
            self.manager.delentity(self.uuid)

    def draw(self, screen):
        self.image.select(x=self.frameno)
        
        super().draw(screen)


class WormParticleSmoke(Entity):
    ID = 'worm:particle_smoke'
    
    TEXTURE = gettiled(modpath('textures/particles/smoke.png'), 3, 1)
    
    GRAVITY = 0
    
    BRAKING = 1
    
    TTL = 5
    
    def __init__(self,
                 manager=None,
                 uuid=None,
                 position=(0, 0)):
        super().__init__(
            manager=manager,
            uuid=uuid,
            position=position,
            velocity=(0, 0))
        
        self.frameno = 0
        
        self.ignore_collision = True
        
        self.lifetime = self.TTL
        
        self.blinktimer = 0
        
        self.image = self.TEXTURE
    
    def update(self, dtime):
        super().update(dtime)
        
        self.lifetime -= dtime
        
        if self.lifetime < self.TTL*7/8:
            self.frameno = 1
        
        if self.lifetime < self.TTL/2:
            self.frameno = 2
        
        if self.lifetime <= 0:
            self.manager.delentity(self.uuid)

    def draw(self, screen):
        self.blinktimer += 1
        
        if self.lifetime < self.TTL/4 and self.blinktimer % 3 == 0:
            return
        
        self.image.select(x=self.frameno)
        
        super().draw(screen)
