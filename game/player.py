from .entity import Entity


class Player(Entity):
    SPEED = 30
    JUMP = 10
    WIDTH = 22
    HEIGHT = 32

    def __init__(self, position=(0, 0), velocity=(0, 0)):
        super().__init__(position, velocity, (self.WIDTH, self.HEIGHT))
        self.left = self.right = self.up = False

    def update_presses(self, left=False, right=False, up=False):
        self.left = left
        self.right = right
        self.up = up

    def update(self, dtime):
        super().update(dtime)

        if self.up and self.on_ground:
            self.yv -= self.JUMP
            self.on_ground = False

        if self.left:
            self.xv -= self.SPEED * dtime
        elif self.right:
            self.xv += self.SPEED * dtime

