from game.meta_manager import MetaManager

from utils.checks import hasattrs

from .biomes import SurfaceBiome
from .ores import CopperOreGen, IronOreGen
from .trees import Tree, Sapling
from .chest import Chest, ChestItem
from .furnace import Furnace
from .anvil import Anvil
from .dungeons import box_dungeon
from .items import register_items
from .crafting import register_craftitems, register_crafts


required_mapgen_attributes = ['add_biome', 'add_ore', 'add_dungeon']
# Attributes that mod will use in init_mapgen.
# If some of them missing, mod can do something.


def on_load(modmanager):
    '''Called every time when starting Game- or Mapgen- Activity
    First argument - ModManager object'''
    Tree.register()
    Sapling.register()
    Chest.register()
    ChestItem.register()
    Furnace.register()
    Anvil.register()
    
    register_items()
    register_craftitems()
    register_crafts()
    
    modmanager.add_handler(init_mapgen=init_mapgen)
    modmanager.add_handler(on_player_join=on_player_join)


def init_mapgen(mg):
    '''Called when starting mapgen. First argument is mapgen object'''
    _, missing = hasattrs(mg, required_mapgen_attributes, True)
    
    if 'add_ore' not in missing:
        mg.add_ore(CopperOreGen(mg))
        mg.add_ore(IronOreGen(mg))
    
    if 'add_biome' not in missing:
        mg.add_biome(SurfaceBiome(mg))
    
    if 'add_dungeon' not in missing:
        mg.add_dungeon(box_dungeon)


def on_player_join(player):
    meta = MetaManager.get()
    
    initstuff = meta.getmeta('gave_initstuff')
    
    if initstuff is None:
        _, initstuff = meta.newmeta('gave_initstuff')
    
    if initstuff.get(player.uuid) is None:
        player.inventory.add_item('main', 'std:copper_pick')
        player.inventory.add_item('main', 'std:copper_axe')
        player.inventory.add_item('main', 'std:hammer')
        
        initstuff[player.uuid] = 1
    
    
