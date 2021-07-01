from game.texture import gettexture, gettiled, animtiled

from game.projectile import Projectile
from game.melee import Swing

from mods.manager import modpath


class Bullet(Projectile):
    ID = 'testing:bullet'
    
    GRAVITY = 0
    
    TEXTURE  = gettexture(modpath('textures/entities/bullet.png'))
    
    TARGET_TAGS = ["hittable"]

    def __init__(self,
                 manager=None,
                 uuid=None,
                 position=(0, 0),
                 angle=0,
                 source_entity=None):
        super().__init__(
            manager=manager,
            uuid=uuid,
            position=position,
            angle=angle,
            source_entity=source_entity)
        
        self.image = self.TEXTURE

    def on_hit_entity(self, entity):
        entity.hurt(10)
        
        self.manager.delentity(self.uuid)


class SwordSwing(Swing):
    ID = 'testing:sword_swing'
    
    SIZE = (64, 64)
    
    OFFSET = (20, -20)
    
    DAMAGE = 15
    
    TEXTURE = gettiled(modpath('textures/entities/sword_swing.png'), 3, 2)
    
    TTL = 0.25
    
    ANIMSPEC = {
        'right': {
            'speed': TTL/3,
            'tiles': [(0, 0), (1, 0), (2, 0)],
        },
        'left': {
            'speed': TTL/3,
            'tiles': [(0, 1), (1, 1), (2, 1)],
        },
    }
    
    def __init__(self, parent,
                 facing_left=True,
                 manager=None,
                 uuid=None):
        super().__init__(
            parent=parent,
            facing_left=facing_left,
            manager=manager,
            uuid=uuid)
        
        self.image = animtiled(self.TEXTURE, self.ANIMSPEC, 'left' if facing_left else 'right')
