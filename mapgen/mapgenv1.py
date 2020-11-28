import math

from .lib.perlin import PerlinNoiseFactory

from .mapgen import Mapgen

from game.block import Block


class MapgenV1(Mapgen):

    def __init__(self, mods, output, width, height, status_v, done_v):
        super().__init__(mods, output, width, height, status_v, done_v)

        self.std_stone = Block.id_by_strid("std:stone")
        self.std_stone_wall = Block.id_by_strid("std:stone_wall")

        self.pnf1 = PerlinNoiseFactory(dimension=1)

        self.pnf2 = PerlinNoiseFactory(dimension=2)

    def run(self):
        super().run()
        
        self.set_status(string="Generating terrain...", done=0)

        for x in range(self.width):
            for y in range(int(self.noise1(x)), self.height):
                self.put_foreground(x, y, self.std_stone)
                self.put_background(x, y, self.std_stone_wall)
            self.set_status(done=(x/self.width)*100)
        
        self.set_status(string="Generating caves...", done=0)

        for y in range(self.height):
            for x in range(self.width):
                if self.get_foreground(x, y) == 0:
                    continue

                if self.noise2(x, y) < -0.2:
                    self.put_foreground(x, y, 0)
            self.set_status(done=(y/self.height)*100)

        for module in self.mods:
            if hasattr(module, "on_generated"):
                module.on_generated(self)
        
        self.set_status(string="Saving the world...", done=0)

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
