import enum

import pygame as pg

_used_textures = []


class Texture:
    TEXTURES = {}

    instances = {}

    def __init__(self, name):
        self.name = name

    def load(self, force=False):
        try:
            if self.TEXTURES.get(self.name) is None or force:
                self.TEXTURES[self.name] = pg.image.load(self.name).convert_alpha()
        except pg.error as e:
            print(f"Could not load {self.name}: {e}")

    def get(self):
        if self.TEXTURES.get(self.name) is None:
            print(f"Warning: texture {self.name} is not preloaded")
            self.load()
        return self.TEXTURES[self.name]


class AnimatedTexture(Texture):

    instances = {}

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
        self.timer += dtime
        if self.timer >= self.speed:
            self.index += 1
            if self.index == len(self.textures):
                self.index = 0


class TiledTexture:

    instances = {}

    def __init__(self, name, tiles_x, tiles_y):
        self.texture = gettexture(name, preload=True)

        self.tiles_x = tiles_x
        self.tiles_y = tiles_y

        self.width = self.texture.get_width()
        self.height = self.texture.get_height()

        self.tile_width = int(self.width/self.tiles_x) + 1
        self.tile_height = int(self.height/self.tiles_y) + 1

    def load(self, force=False):
        self.texture.load(force)

    def get(self, x=0, y=0):
        if x not in range(self.tiles_x) or y not in range(self.tiles_y):
            raise IndexError(
                "invalid position on tile (tile: "
                f"x: 0-{self.tiles_x-1}, y: 0-{self.tiles_y-1}, "
                f"position: x: {x}, y: {y})")

        return self.texture.get().subsurface(
                    (x*self.tile_width,
                     y*self.tile_height,
                     min(self.tile_width, self.width-x*self.tile_width),
                     min(self.tile_height, self.height-x*self.tile_height)))


def gettexture(name, preload=False):
    global _used_textures

    t = None

    if name not in Texture.instances.keys():
        t = Texture(name)
        Texture.instances[name] = t
    else:
        t = Texture.instances[name]

    if preload:
        t.load()
    elif name not in _used_textures:
        _used_textures.append(name)

    return t


def getanimtexture(*names, speed=1, preload=False):
    global _used_textures

    t = None

    if name not in AnimatedTexture.instances.keys():
        t = AnimatedTexture(name)
        AnimatedTexture.instances[name] = t
    else:
        t = AnimatedTexture.instances[name]

    if preload:
        t.load()
    else:
        for name in names:
            if name not in _used_textures:
                _used_textures.append(name)

    return t


def gettiledtexture(name, tiles_x, tiles_y):
    global _used_textures

    t = None

    if name not in TiledTexture.instances.keys():
        t = TiledTexture(name)
        TiledTexture.instances[name] = t
    else:
        t = TiledTexture.instances[name]

    if preload:
        t.load()
    elif name not in _used_textures:
        _used_textures.append(name)

    return t


def load():
    global _used_textures

    for name in _used_textures:
        Texture(name).load(force=True)


def update_animation(dtime):
    global _used_textures

    for texture in AnimatedTexture.instances:
        texture.update(dtime)
