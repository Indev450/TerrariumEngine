from mods.manager import modpath

from game.texture import gettiled
from game.liquid_manager import LiquidDef


class Water(LiquidDef):
    ID = 'std:water'
    
    TEXTURE = gettiled(modpath("textures/liquids/water.png"), 5, 1)
    
    UPDATE_TIME = 0.05
