from .world import World
from .game_object import GameObject


class Entity(GameObject):
    GRAVITY = 25
    BRAKING = 0.7
    MIN_SPEED = 0.2  # Min horizontal speed
    MAX_SPEED = 5
    MAX_FALL = -20  # Maximum of fall speed

    def __init__(self, position=(0, 0), velocity=(0, 0), size=(10, 10)):
        super().__init__(*position, *size)

        self.xv, self.yv = velocity

        self.friction = 20

        self.on_ground = False

        self.world = World.get()

    def update(self, dtime):
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
        block = self.world.is_collide(
            self,
            self.on_collide_x if by_x else self.on_collide_y)

    def on_collide_x(self, block):
        if self.xv > 0:
            self.rect.right = block.rect.left
            self.xv = 0

        if self.xv < 0:
            self.rect.left = block.rect.right
            self.xv = 0

    def on_collide_y(self, block):
        if self.yv > 0:
            self.rect.bottom = block.rect.top
            self.on_ground = True
            self.yv = 0

        if self.yv < 0:
            self.rect.top = block.rect.bottom
            self.yv = 0
