from game.block import Block
from game.texture import gettexture

from mods.manager import modpath


class StoneBlock(Block):
    id = 'std:stone'
    tile = gettexture(modpath("textures/blocks/stone.png"))
    drops = ['std:stone']


class StoneWallBlock(Block):
    id = 'std:stone_wall'
    tile = gettexture(modpath("textures/blocks/stone_wall.png"))


class DirtBlock(Block):
    id = 'std:dirt'
    tile = gettexture(modpath("textures/blocks/dirt.png"))


class DirtWithGrassBlock(Block):
    id = 'std:dirt_with_grass'
    tile = gettexture(modpath("textures/blocks/dirt_with_grass.png"))


class DirtWallBlock(Block):
    id = 'std:dirt_wall'
    tile = gettexture(modpath("textures/blocks/dirt_wall.png"))


StoneBlock.register()
StoneWallBlock.register()
DirtBlock.register()
DirtWithGrassBlock.register()
DirtWallBlock.register()

