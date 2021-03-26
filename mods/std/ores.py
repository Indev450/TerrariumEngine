from mapgen.ore import OreGen

from config import getcfg


config = getcfg()


class CopperOreGen(OreGen):
    id = 'std:copper_ore'
    block = 'std:copper_ore'
    min_y = int(config['mapgen.world_size'][1]*0.1)
    max_y = int(config['mapgen.world_size'][1]*0.8)
