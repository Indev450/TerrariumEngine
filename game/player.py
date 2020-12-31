from .entity import Entity

from .texture import gettiled, animtiled

from .inventory import Inventory


class Player(Entity):
    ID = 'builtin:player'
    
    SPEED = 30
    JUMP = 10
    WIDTH = 20
    HEIGHT = 40

    TEXTURE = gettiled("resources/textures/player/player.png", 3, 3)
    
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
            "tiles": [(0, 1), (1, 1), (2, 1)]
        },
        "walk_right": {
            "speed": 0.2,
            "tiles": [(0, 0), (1, 0), (2, 0)]
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
        
        player.inventory = Inventory().load(save['data']['inventory'])
        
        return player

    def __init__(self, manager=None, uuid=None, position=(0, 0), velocity=(0, 0)):
        super().__init__(manager, uuid, position, velocity, (self.WIDTH, self.HEIGHT))
        self.left = self.right = self.up = False

        self.turned_left = True

        self.image = animtiled(self.TEXTURE, self.ANIMSPEC, "idle_left")
        
        self.inventory = Inventory(self)
        
        self.inventory.set_size('hotbar', 8)
        self.inventory.set_size('main', 8*4)
        self.inventory.set_size('buffer', 1)

        self.selected_item = 0
        
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
        super().update(dtime)

        if self.up and self.on_ground:
            self.yv -= self.JUMP
            self.on_ground = False

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
        }

