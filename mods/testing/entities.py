from game.texture import gettexture

from game.projectile import Projectile

from mods.manager import modpath


class Bullet(Projectile):
    ID = 'testing:bullet'
    
    GRAVITY = 0
    
    TEXTURE  = gettexture(modpath('textures/entities/bullet.png'))

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
