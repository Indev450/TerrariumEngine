from game.item import Item
from game.craft import Craft

from game.texture import gettexture

from mods.manager import modpath

########################################################################
# Craft items
class CopperIngot(Item):
    ID = 'std:copper_ingot'
    image = gettexture(modpath('textures/items/copper_ingot.png'))


class IronIngot(Item):
    ID = 'std:iron_ingot'
    image = gettexture(modpath('textures/items/iron_ingot.png'))


def register_craftitems():
    CopperIngot.register()
    IronIngot.register()


########################################################################
# Crafts
class CraftFurnace(Craft):
    ID = 'std:craft_furnace'
    
    inputs = ['std:stone 20', 'std:wood 10']
    output = 'std:furnace'


class CraftAnvil(Craft):
    ID = 'std:craft_anvil'
    
    inputs = ['std:iron_ingot 15']
    output = 'std:anvil'


class CraftCopperIngot(Craft):
    ID = 'std:craft_copper_ingot'
    TYPE = 'std:furnace'
    
    inputs = ['std:copper_ore 2']
    output = 'std:copper_ingot'


class CraftIronIngot(Craft):
    ID = 'std:craft_iron_ingot'
    TYPE = 'std:furnace'
    
    inputs = ['std:iron_ore 2']
    output = 'std:iron_ingot'


class CraftCopperPick(Craft):
    ID = 'std:craft_copper_pick'
    TYPE = 'std:anvil'
    
    inputs = ['std:copper_ingot 8', 'std:wood 6']
    output = 'std:copper_pick'


class CraftCopperAxe(Craft):
    ID = 'std:craft_copper_axe'
    TYPE = 'std:anvil'
    
    inputs = ['std:copper_ingot 10', 'std:wood 4']
    output = 'std:copper_axe'


class CraftIronPick(Craft):
    ID = 'std:craft_iron_pick'
    TYPE = 'std:anvil'
    
    inputs = ['std:iron_ingot 8', 'std:wood 6']
    output = 'std:iron_pick'


class CraftIronAxe(Craft):
    ID = 'std:craft_iron_axe'
    TYPE = 'std:anvil'
    
    inputs = ['std:iron_ingot 10', 'std:wood 4']
    output = 'std:iron_axe'


class CraftHammer(Craft):
    ID = 'std:craft_hammer'
    
    inputs = ['std:wood 10']
    output = 'std:hammer'


def register_crafts():
    CraftFurnace.register()
    CraftAnvil.register()
    CraftCopperIngot.register()
    CraftIronIngot.register()
    CraftCopperPick.register()
    CraftCopperAxe.register()
    CraftIronPick.register()
    CraftIronAxe.register()
    CraftHammer.register()
