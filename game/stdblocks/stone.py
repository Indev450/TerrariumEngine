import pygame as pg

from game.block import Block

from game.texture import gettexture


class StoneBlock(Block):
    tile = gettexture("resources/textures/blocks/stone.png")


class StoneWallBlock(Block):
    tile = gettexture("resources/textures/blocks/stone_wall.png")


Block.register("std:stone", StoneBlock)
Block.register("std:stone_wall", StoneWallBlock)
