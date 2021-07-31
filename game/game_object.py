import pygame as pg

from .camera import Camera

from game.texture import getblank


class GameObject(pg.sprite.Sprite):
    """Most base game object. Has basic implementation of draw()"""

    def __init__(self, x, y, width, height, angle=0):
        super().__init__()

        self.rect = pg.Rect(x, y, width, height)
        # All game objects should have a rect

        self.image = None

        self.camera = Camera.get()
        
        self.angle = 0

    def draw(self, screen):
        """Draw object on the screen. Checks is it in the camera
        bounds, and if not - skips drawing"""
        info = pg.display.Info()
        offset_x, offset_y = self.camera.get_position()
        draw_x = self.rect.x - offset_x
        draw_y = self.rect.y - offset_y
        if (-self.rect.width <= draw_x <= info.current_w and
           -self.rect.height <= draw_y <= info.current_h):
            screen.blit(pg.transform.rotate(self.image.get(), self.angle), (draw_x, draw_y))
    
    def get_position(self):
        return self.rect.topleft
