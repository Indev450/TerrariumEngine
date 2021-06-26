from game.texture import gettexture
from game.sound import getsound

from game.tree import TreeDef

from mods.manager import modpath


class Tree(TreeDef):
    ID = 'std:tree'
    
    TEXTURE = gettexture(modpath('textures/entities/tree.png'))
    
    SND_CHOP = getsound(modpath('sounds/tree_chop.wav'))
    SND_CHOPPED = getsound(modpath('sounds/tree_chop.wav'))
