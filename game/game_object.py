import pygame as pg

from .camera import Camera

from game.texture import getblank


class GameObject(pg.sprite.Sprite):
    """Most base game object. Has basic implementation of init_graphics() and draw().
    Other game object types should redefine them."""

    def __init__(self, x, y, width, height):
        super().__init__()

        self.rect = pg.Rect(x, y, width, height)
        # All game objects should have a rect

        self.image = getblank(width, height)

        self.camera = Camera.get()

    def draw(self, screen):
        info = pg.display.Info()
        offset_x, offset_y = self.camera.get_position()
        draw_x = self.rect.x - offset_x
        draw_y = self.rect.y - offset_y
        if (-self.rect.width <= draw_x <= info.current_w and
           -self.rect.height <= draw_y <= info.current_h):
            screen.blit(self.image.get(), (draw_x, draw_y))
            return 1
        return 0
