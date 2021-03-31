import math
import array

from lib.perlin import PerlinNoiseFactory

from game.block import BlockDefHolder, Block

from .biome import Biome


class OreGen(Biome):
    id = 'builtin:ore_base'
    name = 'Ore'
    block = None
    layer = 0
    min_noise = 0.7
    
    min_y = 0
    max_y = 0
    
    def __init__(self, mapgen):
        super().__init__(mapgen)
        
        self.noise = PerlinNoiseFactory(2)
        
        self.noise_scale_x = 0.8
        self.noise_scale_y = 0.4
        
        self.blockid = BlockDefHolder.id_by_strid(self.block)
    
    def get_bounds(self, world_width, world_height):
        return (0, self.min_y, world_width, min(self.max_y, world_height))
    
    def get_blocks(self, value, blocks):
        return (
            blocks[0] if self.layer != 0 or value < self.min_noise or blocks[0] == 0 else self.blockid,
            blocks[1] if self.layer != 1 or value < self.min_noise or blocks[1] == 0 else self.blockid,
            blocks[2] if self.layer != 2 or value < self.min_noise or blocks[2] == 0 else self.blockid,
        )
    
    def get_blocks_at(self, x, y, orignoise, blocks):
        noise = math.tan(self.noise(
            x/(self.noise_scale_x*Block.WIDTH),
            y/(self.noise_scale_y*Block.HEIGHT)))
        
        return self.get_blocks(noise, blocks)
