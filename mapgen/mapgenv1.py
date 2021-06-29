import math

from .mapgen import Mapgen

from lib.perlin import PerlinNoiseFactory

from game.block import BlockDefHolder, Block

from mods.manager import ModManager


class MapgenV1(Mapgen):

    def __init__(self, mods, output, width, height, status_v, done_v):
        super().__init__(mods, output, width, height, status_v, done_v)

        self.std_stone = BlockDefHolder.id_by_strid("std:stone")
        self.std_stone_wall = BlockDefHolder.id_by_strid("std:stone_wall")

        self.pnf1 = PerlinNoiseFactory(dimension=1)

        self.pnf2 = PerlinNoiseFactory(dimension=2)
        
        self.noise_scale_x = 2
        self.noise_scale_y = 1
        
        self.biomes = {}
        self.ores = {}
        self.dungeons = []

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
            
        self.set_status(string="Generating biomes...", done=0)
        
        biomes = len(self.biomes.keys())
        biomes_processed = 0
        
        for biome in self.biomes.keys():
            self.process_biome(biome)
            
            biomes_processed += 1
            self.set_status(done=(biomes_processed/biomes)*100)
        
        self.set_status(string="Generating ores...", done=0)
        
        self.biomes = self.ores  # Ores are biomes to, but they must be processed after all biomes
        
        ores = len(self.ores.keys())
        ores_processed = 0
        
        for ore in self.ores.keys():
            self.process_biome(ore)
            
            ores_processed += 1
            self.set_status(done=(ores_processed/ores)*100)
        
        self.set_status(string="Adding dungeons...", done=0)
        
        dungeons = len(self.dungeons)
        dungeons_processed = 0
        
        for dungeon in self.dungeons:
            dungeon(self)
            
            dungeons_processed += 1
            self.set_status(done=(dungeons_processed/dungeons)*100)
        
        self.set_status(string="Saving the world...", done=0)

        self.save()

    def noise2(self, x, y):
        return math.tan(self.pnf2(
            x/(self.noise_scale_x*Block.WIDTH),
            y/(self.noise_scale_y*Block.HEIGHT)))

    def noise1(self, x):
        v = math.tan(self.pnf1(x/(self.noise_scale_x*Block.WIDTH)))
        return self.height*0.3 + 10*v
    
    def add_biome(self, biome):
        self.biomes[biome.id] = biome
    
    def add_ore(self, ore):
        self.ores[ore.id] = ore
    
    def add_dungeon(self, cb):
        self.dungeons.append(cb)
    
    def process_biome(self, id):
        biome = self.biomes.get(id)
        
        if biome is None:
            print(f'Error: could not process biome {id}: no such biome')
            return
        
        left, top, right, bottom = biome.get_bounds(self.width, self.height)
        
        for x in range(left, right):
            for y in range(top, bottom):
                try:
                    self.put_blocks(x, y, biome.get_blocks_at(
                        x, y, self.noise2(x, y), self.get_blocks(x, y)))
                except IndexError:
                    pass


def get_mapgen():
    return MapgenV1
