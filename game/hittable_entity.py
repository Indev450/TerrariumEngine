from .entity import Entity


class HittableEntity(Entity):
    """Some entity that takes damage"""
    HP_MAX = 100
    
    SND_HURT = None
    SND_DEATH = None
    
    DO_FALL_DAMAGE = True
    FALL_DAMAGE = 50  # Damage per second increased while falling
    FALL_DAMAGE_SPEED = 15  # How fast entity should fall to take damage
    
    IMMUNE_TO = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hp = self.HP_MAX
        self.inv_timer = 0
        self.fall_damage = 0
        
        # Separe set to allow mutability (some resistance effects for example)
        self.immune_to = set(self.IMMUNE_TO)
    
    def update(self, dtime):
        super().update(dtime)
        
        self.inv_timer -= dtime
        
        if self.DO_FALL_DAMAGE:
            self.update_falldamage(dtime)
        
        for liquid in self.collide_liquids:
            if liquid.DAMAGE != 0:
                self.hurt((liquid.DAMAGE, liquid.DAMAGE_TYPE), inv_time=1)
    
    def update_falldamage(self, dtime):
        if not self.on_ground:
            if self.yv*self.liquid_resistance > self.FALL_DAMAGE_SPEED:
                self.fall_damage += self.FALL_DAMAGE * dtime
            
            else:
                # If entity slowed down (in water, for example), cancel fall damage
                self.fall_damage = 0
        
        if self.on_ground and self.fall_damage:
            damage = int(self.fall_damage)
            
            if damage >= 5:
                self.hurt(damage, knockback=0, inv_time=0.2)
            
            self.fall_damage = 0
    
    def hurt(self, damage, entity=None, knockback=0, inv_time=0):
        if isinstance(damage, tuple):
            damage, damage_type = damage
        
        else:
            damage, damage_type = damage, "normal"
        
        if self.inv_timer > 0 or self.hp <= 0 or damage_type in self.immune_to:
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
