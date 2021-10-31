from .entity import Entity

from .texture import gettiled, animtiled

from .sound import getsound

from .inventory import Inventory

from .meta_manager import MetaManager

from utils.weakobj import WeakObject

from config import getcfg


config = getcfg()


class Player(Entity):
    ID = 'builtin:player'
    
    SPEED = config["player.speed"]
    JUMP = config["player.jump"]
    JUMP_KEEP = config["player.jump_keep"]
    WIDTH = config["player.size"][0]
    HEIGHT = config["player.size"][1]

    TEXTURE = gettiled("resources/textures/player/player.png", 3, 3)
    
    SND_HURT = getsound(config["player.hurt_sound"])
    SND_DEATH = getsound(config["player.death_sound"])
    
    ANIMSPEC = {
        "idle_left": {
            "speed": 1,
            "tiles": [(0, 1)]
        },
        "idle_right": {
            "speed": 1,
            "tiles": [(0, 0)]
        },
        "walk_left": {
            "speed": 0.2,
            "tiles": [(0, 1), (1, 1), (0, 1), (2, 1)]
        },
        "walk_right": {
            "speed": 0.2,
            "tiles": [(0, 0), (1, 0), (0, 0), (2, 0)]
        },
        "jump_left": {
            "speed": 1,
            "tiles": [(1, 2)]
        },
        "jump_right": {
            "speed": 1,
            "tiles": [(0, 2)]
        },
    }
    
    @classmethod
    def from_save(cls, manager, uuid, save):
        player = super().from_save(manager, uuid, save)
        
        player.inventory.load(save['data']['inventory'])
        
        player.hp = save['data'].get('hp', 100)
        
        return player

    def __init__(self, manager=None, uuid=None, position=(0, 0), velocity=(0, 0)):
        super().__init__(manager, uuid, position, velocity, (self.WIDTH, self.HEIGHT))
        self.left = self.right = self.up = False

        self.turned_left = True

        self.image = animtiled(self.TEXTURE, self.ANIMSPEC, "idle_left")
        
        self.inventory = Inventory(WeakObject(self))
        
        self.inventory.set_size('hotbar', 8)
        self.inventory.set_size('main', 8*4)
        self.inventory.set_size('buffer', 1)

        self.selected_item = 0
        
        self.fall_damage = 0
        
        self.hp = self.max_hp = config["player.max_hp"]

        self.blinking_timer = 0  # How long player have to blink
        self.blinking_timer2 = 0  # For blinking effect
        
        self.respawn_timer = 0
        
        self.respawn_pos = (0, 0)
        
        spawn = MetaManager.get().getmeta('spawnpoint')
        
        if spawn is not None:
            self.respawn_pos = spawn['position']
        
        self.add_tag('player')

    def update_presses(self, left=False, right=False, up=False):
        if left:
            self.turned_left = True
            self.set_animation("walk_left")
        elif right:
            self.turned_left = False
            self.set_animation("walk_right")

        self.left = left
        self.right = right
        self.up = up
    
    def set_animation(self, name):
        if self.image.get_animation() != name:
            self.image.set_animation(name)

    def update(self, dtime):
        if self.hp <= 0:
            self.respawn_timer -= dtime
            
            if self.respawn_timer <= 0:
                self.respawn()
            
            return
        
        super().update(dtime)
        
        if self.blinking_timer > 0:
            self.blinking_timer -= dtime
            
            if self.blinking_timer <= 0:
                self.blinking = False
                self.blinking_timer2 = 0
        
        if not self.on_ground and self.yv > 15:
            self.fall_damage += 50 * dtime
        
        if self.on_ground:
            damage = int(self.fall_damage)
            
            if damage:
                self.hurt(damage, knockback=0)
            
            self.fall_damage = 0

        if self.up:
            if self.on_ground:
                self.yv -= self.JUMP
                self.on_ground = False
            
            if self.yv < -5:
                self.yv -= self.JUMP_KEEP * dtime

        if self.left:
            self.xv -= self.SPEED * dtime
        if self.right:
            self.xv += self.SPEED * dtime
        
        if self.xv == 0 and self.on_ground:
            self.set_animation("idle_" + ("left" if self.turned_left else "right"))
    
    def get_inventory(self):
        return self.inventory
    
    def on_save(self):
        return {
            'inventory': self.inventory.dump(),
            'hp': self.hp,
        }
    
    def hurt(self, damage, entity=None, knockback=5, invulnerable_time=1):
        if self.blinking_timer > 0 or self.hp <= 0:
            return
        
        self.blinking_timer = invulnerable_time
        
        self.hp -= damage
        
        if self.hp <= 0:
            self.SND_DEATH.play(0)
            self.respawn_timer = 5
            return
        
        self.SND_HURT.play(0)
        
        if entity is not None:
            if self.rect.x > entity.rect.x:
                self.xv = knockback
            else:
                self.xv = -knockback
        
        self.yv = -knockback
    
    def respawn(self):
        self.hp = self.max_hp
        
        self.rect.topleft = self.respawn_pos
    
    def draw(self, screen):
        if self.hp <= 0:
            return
        
        if self.blinking_timer > 0:
            self.blinking_timer2 += 1
            
            if self.blinking_timer2 % 3 == 0:
                return
        
        super().draw(screen)
    
    '''
    def collide(self, by_x):
        """Checks collision for one dimension"""
        if by_x:
            self.rect.height -= 17
            self.world.is_collide(self, self._on_collide_x)
            self.rect.height += 17
        
        else:
            self.world.is_collide(self, self._on_collide_y)
    ''' # TODO - Do stairs effect normally
