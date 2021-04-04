import random

from time import time

from game.texture import gettexture
from game.parallax import Parallax, ParallaxElement

from config import getcfg


config = getcfg()


class DefaultParallax(Parallax):
    CLOUD_COUND = 16
    
    def __init__(self):
        super().__init__()
        
        self.add_object(Sun(self))
        
        for i in range(self.CLOUD_COUND):
            self.add_object(Cloud(self, Cloud.size[0]*i/2))
            self.add_object(CloudForeground(self, Cloud.size[0]*i/2))


class Sun(ParallaxElement):
    texture = gettexture('resources/textures/parallax/sun.png')
    offset = (10, 10)
    size = (256, 256)
    order = 10
    OFFSET_Y = -1

    def get_position(self):
        x, y = super().get_position()
        
        x += self.offset[0]
        y += self.offset[1]
        
        return (x, y)


class Cloud(ParallaxElement):
    texture = gettexture('resources/textures/parallax/cloud.png')
    size = (256, 128)
    speed = 50
    order = 9
    
    OFFSET_Y = -5
    OFFSET_X = -10
    BASE_OFFSET_Y = 500
    
    def __init__(self, parallax, offx):
        self.starttime = time() - offx/self.speed + self.size[0]/self.speed
        self.rand_y = self.size[1] * random.random() / 2
        self.parallax = parallax
        
        super().__init__(parallax)
    
    def get_position(self):
        x, y = super().get_position()
        camx, _ = self.camera.get_position()
        
        offx = self.speed*(time()-self.starttime)
        
        if x + offx > config['app.resolution'][0] + camx:
            self.starttime = time() + self.size[0]/self.speed
        
        return x + offx, y + self.rand_y


class CloudForeground(Cloud):
    texture = gettexture('resources/textures/parallax/cloud_foreground.png')
    order = 8
    OFFSET_X = -15
    OFFSET_Y = -10
    BASE_OFFSET_Y = 700
