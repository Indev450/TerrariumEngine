import pygame as pg

from game.block import Block

from game.texture import gettexture


class StoneBlock(Block):
    tile = gettexture("resources/textures/blocks/stone16x16.png")


Block.register("std:stone", StoneBlock)
