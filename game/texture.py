import enum

import pygame as pg

from utils.color import randcolor

_used_textures = []


class Texture:
    """Most base texture class. 
    It's basicly just a wrapper for pygame.Surface"""

    TEXTURES = {}  # Loaded surfaces

    instances = {}  # Texture objects

    def __init__(self, name):
        self.name = name

    def load(self, force=False):
        """Load surface. Should be called after pygame.display.set_mode()"""
        try:
            if self.TEXTURES.get(self.name) is None or force:
                self.TEXTURES[self.name] = pg.image.load(self.name).convert_alpha()
        except pg.error as e:
            print(f"Could not load {self.name}: {e}")
        except FileNotFoundError:
            print(f'Error: could not load texture {self.name}')
            self.TEXTURES[self.name] = getblank(16, 16).image

    def get(self):
        """Get surface object"""
        if self.TEXTURES.get(self.name) is None:
            print(f"Warning: texture {self.name} is not preloaded")
            self.load()
        return self.TEXTURES[self.name]


class AnimatedTexture(Texture):
    """Animated texture contains few references to Texture objects
    which are containing animation frames. Better use AnimatedTiledTexture"""

    instances = []

    def __init__(self, names, speed=1):
        self.textures = [gettexture(name) for name in names]

        self.speed = speed

        self.timer = 0

        self.index = 0

    def load(self, force=False):
        for texture in self.textures:
            texture.load(force)

    def get(self):
        return self.textures[self.index].get()

    def update(self, dtime):
        """Update animation"""
        self.timer += dtime
        if self.timer >= self.speed:
            self.index += 1
            self.timer = 0
            if self.index == len(self.textures):
                self.index = 0


class RotateTexture(Texture):
    
    def __init__(self, texture, rotate_time, start_angle, end_angle):
        self.texture = texture
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.rotate_time = rotate_time
        self.timer = 0
        
        AnimatedTexture.instances.append(self)
    
    def load(self, force=False):
        self.texture.load(force)
    
    def get(self):
        angle = self.get_angle()
        surf = pg.transform.rotate(self.texture.get(), abs(angle))
        
        if angle < 0:
            surf = pg.transform.flip(surf, True, False)
        
        return surf
        
    
    def get_angle(self):
        return self.start_angle + (self.timer / self.rotate_time) * (self.end_angle - self.start_angle)
    
    def update(self, dtime):
        self.timer += dtime
        
        if self.timer > self.rotate_time:
            self.timer = 0


class TiledTexture(Texture):
    """Very useful texture for using tile maps.
    Has interface to easily get some textures"""

    def __init__(self, name, tiles_x, tiles_y):
        self.texture = gettexture(name)

        self.tiles_x = tiles_x
        self.tiles_y = tiles_y

        self.width = 0
        self.height = 0

        self.tile_width = 0
        self.tile_height = 0
        
        self.current_x = self.current_y = 0

    def load(self, force=False):
        self.texture.load(force)

        self.width = self.texture.get().get_width()
        self.height = self.texture.get().get_height()

        self.tile_width = self.width//self.tiles_x
        self.tile_height = self.height//self.tiles_y
        
    def select(self, x=None, y=None):
        x = x if x is not None else self.current_x
        y = y if y is not None else self.current_y
        
        self.current_x = x
        self.current_y = y

    def get(self, x=None, y=None):
        """Get tile at given position"""
        x = x if x is not None else self.current_x
        y = y if y is not None else self.current_y
        
        if x not in range(self.tiles_x) or y not in range(self.tiles_y):
            raise IndexError(
                "invalid position on tile (tile: "
                f"x: 0-{self.tiles_x-1}, y: 0-{self.tiles_y-1}, "
                f"position: x: {x}, y: {y})")

        return self.texture.get().subsurface(
                    (x*self.tile_width,
                     y*self.tile_height,
                     min(self.tile_width, self.width-x*self.tile_width),
                     min(self.tile_height, self.height-y*self.tile_height)))


class AnimatedTiledTexture(AnimatedTexture):
    """Most usefu wrapper for making animations for entities"""

    def __init__(self, texture, animspec, current="idle"):
        self.texture = texture

        self.animspec = animspec

        self.current_name = current
        
        self.index = 0
        self.timer = 0

        self.speed = animspec[current]["speed"]
    
    def load(self, force=False):
        self.texture.load(force)
    
    def set_animation(self, name):
        """Set current animation by its name"""
        if self.animspec.get(name) is None:
            raise NameError(f"animation {name} does not exists")
        
        self.current_name = name
        self.index = 0

        self.speed = self.animspec[name]["speed"]
    
    def set_speed(self, speed=None):
        self.speed = speed or self.animspec[self.current_name]["speed"]
    
    def get_animation(self):
        """Get current animation name"""
        return self.current_name

    def get(self):
        return self.texture.get(
            *self.animspec[self.current_name]["tiles"][self.index])
    
    def update(self, dtime):
        self.timer += dtime
        if self.timer >= self.speed:
            self.index += 1
            self.timer = 0
            if self.index == len(self.animspec[self.current_name]["tiles"]):
                self.index = 0


class BlankTexture(Texture):
    """Blank textures are useful for testing"""

    def __init__(self, size, color, alpha=False):
        self.image = pg.Surface(size)
        self.image.fill(color)
        
        self.alpha = alpha

    def load(self, force=False):
        if self.alpha:
            self.image = self.image.convert_alpha()

    def get(self):
        return self.image


def gettexture(name, preload=False):
    """Create Texture object which will load and convert pygame.Surface
    when it become possible"""

    global _used_textures

    t = None

    if name not in Texture.instances.keys():
        t = Texture(name)
        Texture.instances[name] = t
    else:
        t = Texture.instances[name]

    if preload:
        t.load()
    else:
        _used_textures.append(t)

    return t


def getblank(*size):
    """Get random-colorized blank texture"""
    return BlankTexture(size, pg.Color(randcolor()))


def gettransparent(*size):
    """Void texture"""
    t = BlankTexture(size, pg.Color(0, 0, 0, 0), True)
    
    _used_textures.append(t)
    
    return t


def getanimated(*names, speed=1, preload=False):
    """Create AnimatedTexture object. Better use AnimatedTiledTexture
    (animtiled)"""
    global _used_textures

    t = AnimatedTexture(names, speed)
    
    AnimatedTexture.instances.append(t)

    if preload:
        t.load()
    else:
        _used_textures.append(t)

    return t


def gettiled(name, tiles_x, tiles_y, preload=False):
    """Load tile map."""
    global _used_textures

    t = TiledTexture(name, tiles_x, tiles_y)

    if preload:
        t.load()
    else:
        _used_textures.append(t)

    return t


def animtiled(texture, animspec, current="idle"):
    """Apply animspec to TiledTexture.
    anipspec is a dict with that structure:
    {
        "animation_name": {
            "speed": 0.5,  # Time for each frame
            "tiles": [],  # List of tuples (tile positions)
        },
        ...
    }"""

    t = AnimatedTiledTexture(texture, animspec, current)

    AnimatedTexture.instances.append(t)

    _used_textures.append(t)

    return t


def load(force=False):
    """Try to load every texture. If force is true, every texture will
    be loaded even if it already loaded"""
    global _used_textures

    for texture in _used_textures:
        texture.load()


def reload():
    """Reload textures"""
    load(force=True)


def update_animation(dtime):
    """Update all animated textures"""
    for texture in AnimatedTexture.instances:
        texture.update(dtime)
