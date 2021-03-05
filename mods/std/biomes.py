from utils.coords import neighbours

from game.block import Block

from mapgen.biome import Biome


class SurfaceBiome(Biome):
    id = 'std:surface'
    name = 'Surface'
    
    def __init__(self, mapgen):
        super().__init__(mapgen)
        
        self.dirt = Block.id_by_strid('std:dirt')
        self.dirt_with_grass = Block.id_by_strid('std:dirt_with_grass')
        self.dirt_wall = Block.id_by_strid('std:dirt_wall')

    def get_bounds(self, world_width, world_height):
        return (0, 0, world_width, int(world_height/3))
    
    def get_blocks_at(self, x, y, orignoise, blocks):
        grass = False
        
        for nx, ny in neighbours(x, y):
            if self.mapgen.get_foreground(nx, ny) == 0:
                grass = True
                break
        
        return (
            blocks[0] if blocks[0] == 0 or orignoise > 0.4 else self.dirt_with_grass if grass else self.dirt,
            blocks[1],
            blocks[2] if blocks[2] == 0 or orignoise > 0.4 else self.dirt_wall,
        )
