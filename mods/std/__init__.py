from utils.checks import hasattrs

from .biomes import SurfaceBiome

required_mapgen_attributes = []
# Attributes that mod will use in init_mapgen.
# If some of them missing, mod can do something.


def on_load(modmanager):
    '''Called every time when starting Game- or Mapgen- Activity
    First argument - ModManager object'''
    import mods.std.blocks
    import mods.std.items
    
    modmanager.add_handler(init_mapgen=init_mapgen)


def init_mapgen(mg):
    '''Called when starting mapgen. First argument is mapgen object'''
    _, missing = hasattrs(mg, required_mapgen_attributes, True)
    
    if 'add_ore' not in missing:
        pass
    
    if 'add_biome' not in missing:
        mg.add_biome(SurfaceBiome(mg))
