from utils.checks import hasattrs

from .biomes import SurfaceBiome
from .ores import CopperOreGen


required_mapgen_attributes = ['add_biome', 'add_ore']
# Attributes that mod will use in init_mapgen.
# If some of them missing, mod can do something.


def on_load(modmanager):
    '''Called every time when starting Game- or Mapgen- Activity
    First argument - ModManager object'''
    modmanager.add_handler(init_mapgen=init_mapgen)


def init_mapgen(mg):
    '''Called when starting mapgen. First argument is mapgen object'''
    _, missing = hasattrs(mg, required_mapgen_attributes, True)
    
    if 'add_ore' not in missing:
        mg.add_ore(CopperOreGen(mg))
    
    if 'add_biome' not in missing:
        mg.add_biome(SurfaceBiome(mg))
