from game.texture import gettexture, RotateTexture

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
    
    OFFSET = (13, -20)
    
    DAMAGE = 15
    
    TEXTURE = gettexture(modpath('textures/entities/sword_swing.png'))
    
    TTL = 0.25
    
    def __init__(self, parent,
                 facing_left=True,
                 manager=None,
                 uuid=None):
        super().__init__(
            parent=parent,
            facing_left=facing_left,
            manager=manager,
            uuid=uuid)
        
        self.image = RotateTexture(self.TEXTURE, self.TTL, 0, 90 if facing_left else -90)
