from .entity import Entity


class HittableEntity(Entity):
    """Some entity that takes damage"""
    HP_MAX = 100
    
    SND_HURT = None
    SND_DEATH = None
    
    DO_FALL_DAMAGE = True
    FALL_DAMAGE = 50  # Damage per second increased while falling
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hp = self.HP_MAX
        self.inv_timer = 0
    
    def update(self, dtime):
        super().update(dtime)
        
        self.inv_timer -= dtime
        
        if self.DO_FALL_DAMAGE:
            self.update_falldamage(dtime)
    
    def update_falldamage(self, dtime):
        if not self.on_ground and self.yv > 15:
            self.fall_damage += self.FALL_DAMAGE * dtime
        
        if self.on_ground:
            damage = int(self.fall_damage)
            
            if damage >= 5:
                self.hurt(damage, knockback=0, inv_time=0.2)
            
            self.fall_damage = 0
    
    def hurt(self, damage, entity=None, knockback=0, inv_time=0):
        if self.inv_timer > 0 or self.hp <= 0:
            return
        
        self.inv_timer = inv_time
        
        self.hp -= damage
        
        if self.hp <= 0:
            self.hp = 0  # For case when hp < 0
            self.SND_DEATH.play_at(self.rect.center)
            self.on_death(entity)
        
        else:
            self.SND_HURT.play_at(self.rect.center)
            
            self.do_knockback(knockback, entity)
    
    def do_knockback(self, knockback, entity=None):
        if entity is not None:
            if self.rect.x > entity.rect.x:
                self.xv = knockback
            else:
                self.xv = -knockback
        
        self.yv = -knockback

    def on_damage(self, damage, entity):
        pass

    def on_death(self, entity):
        pass
