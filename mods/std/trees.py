from game.texture import gettexture
from game.sound import getsound

from .tree_api import TreeDef
from .sapling_api import SaplingDef

from mods.manager import modpath


class Tree(TreeDef):
    ID = 'std:tree'
    
    TEXTURE = gettexture(modpath('textures/entities/tree.png'))
    
    SND_CHOP = getsound(modpath('sounds/tree_chop.wav'))
    SND_CHOPPED = getsound(modpath('sounds/tree_chop.wav'))
    
    drops = ["std:wood 8", "std:sapling 2"]


class Sapling(SaplingDef):
    ID = 'std:sapling'
    TEXTURE = gettexture(modpath('textures/entities/sapling.png'))
    
    ITEM_TEXTURE = gettexture(modpath('textures/items/sapling.png'))
    
    TREE = 'std:tree'

