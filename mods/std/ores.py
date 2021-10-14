from mapgen.ore import OreGen

from config import getcfg


config = getcfg()


class CopperOreGen(OreGen):
    id = 'std:copper_ore'
    block = 'std:copper_ore'
    min_y = int(config['mapgen.world_size'][1]*0.3)
    max_y = int(config['mapgen.world_size'][1]*0.7)
    
    min_noise = 0.85


class IronOreGen(OreGen):
    id = 'std:iron_ore'
    block = 'std:iron_ore'
    min_y = int(config['mapgen.world_size'][1]*0.35)
    max_y = int(config['mapgen.world_size'][1]*0.8)
    
    min_noise = 0.9


class GoldOreGen(OreGen):
    id = 'std:gold_ore'
    block = 'std:gold_ore'
    min_y = int(config['mapgen.world_size'][1]*0.55)
    max_y = int(config['mapgen.world_size'][1]*0.9)
    
    min_noise = 0.93
