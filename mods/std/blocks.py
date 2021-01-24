from game.block import Block
from game.texture import gettexture, gettiled

from mods.manager import modpath


class StoneBlock(Block):
    id = 'std:stone'
    drawtype = 'tiled'
    tile = gettiled(modpath("textures/blocks/stone.png"), 8, 2)
    drops = ['std:stone']


class StoneWallBlock(Block):
    id = 'std:stone_wall'
    tile = gettexture(modpath("textures/blocks/stone_wall.png"))


class DirtBlock(Block):
    id = 'std:dirt'
    drawtype = 'tiled'
    tile = gettiled(modpath("textures/blocks/dirt.png"), 8, 2)


class DirtWithGrassBlock(Block):
    id = 'std:dirt_with_grass'
    drawtype = 'tiled'
    tile = gettiled(modpath("textures/blocks/grassdirt.png"), 8, 2)


class DirtWallBlock(Block):
    id = 'std:dirt_wall'
    tile = gettexture(modpath("textures/blocks/dirt_wall.png"))
