from .world import World
from .game_object import GameObject


class Entity(GameObject):
    registered = {}
    ID = ''
    
    GRAVITY = 25  # Fall speed
    BRAKING = 0.7  # To avoid endless motion of object
    MIN_SPEED = 0.2  # Minimum horizontal speed
    MAX_SPEED = 5  # Maximum horizontal speed
    MAX_FALL = -20  # Maximum of fall speed
    
    @classmethod
    def register(cls):
        if cls.registered.get(cls.ID) is not None:
            traceback.print_stack()
            print(f'Warning: entity {cls.ID} already registered')
        cls.registered[cls.ID] = cls
    
    @classmethod
    def get(cls, key):
        return cls.registered.get(key)

    @classmethod
    def from_save(cls, save):
        return cls(position=save['entity']['position'],
                   velocity=save['entity']['velocity'])

    def __init__(self, position=(0, 0), velocity=(0, 0), size=(10, 10)):
        super().__init__(*position, *size)

        self.xv, self.yv = velocity

        self.friction = 20

        self.on_ground = False

        self.world = World.get()

    def update(self, dtime):
        """Called every frame. Updates entitys physics"""
        acceleration = self.xv - self.xv*self.BRAKING

        self.xv -= acceleration * dtime * self.friction

        if abs(self.xv) < self.MIN_SPEED:
            self.xv = 0
        elif self.xv > self.MAX_SPEED:
            self.xv = self.MAX_SPEED
        elif self.xv < -self.MAX_SPEED:
            self.xv = -self.MAX_SPEED

        if not self.on_ground:
            self.yv += self.GRAVITY * dtime

            if self.yv < self.MAX_FALL:
                self.yv = self.MAX_FALL

        self.on_ground = False
        self.rect.y += self.yv
        self.collide(False)

        self.rect.x += self.xv
        self.collide(True)
    
    def collide(self, by_x):
        """Checks collision for one dimension"""
        self.world.is_collide(
            self,
            self._on_collide_x if by_x else self._on_collide_y)
    
    def on_save(self):
        """Called when game saves. Can be used to save
        some meta, or self. Should return json-supporting
        object or None"""
        pass
    
    def get_velocity(self):
        return self.xv, self.yv

    def _on_collide_x(self, block):
        """Collide callback for x"""
        if self.xv > 0:
            self.rect.right = block.rect.left
            self.xv = 0

        if self.xv < 0:
            self.rect.left = block.rect.right
            self.xv = 0

    def _on_collide_y(self, block):
        """Collide callback for y"""
        if self.yv > 0:
            self.rect.bottom = block.rect.top
            self.on_ground = True
            self.yv = 0

        if self.yv < 0:
            self.rect.top = block.rect.bottom
            self.yv = 0
