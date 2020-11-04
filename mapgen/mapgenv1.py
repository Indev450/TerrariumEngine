import math

from .lib.perlin import PerlinNoiseFactory

from .mapgen import Mapgen

from game.block import Block


class MapgenV1(Mapgen):

    def __init__(self, mods, output, width, height):
        super().__init__(mods, output, width, height)

        self.stdstone = Block.id_by_strid("std:stone")

        self.pnf1 = PerlinNoiseFactory(dimension=1)

        self.pnf2 = PerlinNoiseFactory(dimension=2)

    def run(self):
        for x in range(self.width):
            for y in range(int(self.noise1(x)), self.height):
                self.blocks[y][x] = self.stdstone

        for y in range(self.height):
            for x in range(self.width):
                if self.blocks[y][x] == 0:
                    continue

                if self.noise2(x, y) < -0.2:
                    self.blocks[y][x] = 0

        for module in self.mods:
            if hasattr(module, "on_generated"):
                module.on_generated(self)

        self.save()

    def noise2(self, x, y):
        return math.tan(self.pnf2(
            x/self.width*Block.WIDTH,
            y/self.height*Block.HEIGHT))

    def noise1(self, x):
        v = math.tan(self.pnf1(x/self.width))
        return self.height*0.3 + 10*v


def get_mapgen():
    return MapgenV1
