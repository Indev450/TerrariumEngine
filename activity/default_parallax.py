import random

from time import time

from game.texture import gettexture
from game.parallax import Parallax, ParallaxElement

from config import getcfg


config = getcfg()


class DefaultParallax(Parallax):
    CLOUD_COUND = 30
    
    def __init__(self):
        super().__init__()
        
        self.add_object(Sun(self))
        
        for i in range(self.CLOUD_COUND):
            self.add_object(Cloud(self, True))


class Sun(ParallaxElement):
    texture = gettexture('resources/textures/parallax/sun.png')
    offset = (10, 10)
    size = (256, 256)
    order = 1

    def get_position(self):
        x, y = super().get_position()
        
        x += self.offset[0]
        y += self.offset[1]
        
        return (x, y)


class Cloud(ParallaxElement):
    texture = gettexture('resources/textures/parallax/cloud.png')
    size = (256, 128)
    speed = 50
    order = 0
    
    def __init__(self, parallax, init=False):
        self.rand_y = random.random()*config['app.resolution'][1]
        self.rand_x = random.randint(-600, config['app.resolution'][0] if init else -self.size[0])
        self.starttime = time()
        self.parallax = parallax
        
        super().__init__(parallax)
    
    def get_position(self):
        x, y = super().get_position()
        
        offx = self.speed*(time()-self.starttime) + self.rand_x
        
        if offx > config['app.resolution'][0]:
            self.starttime = time()
            self.rand_y = random.random()*config['app.resolution'][1]
            self.rand_x = random.randint(-600, -self.size[0])
        
        return x + offx, y + self.rand_y
