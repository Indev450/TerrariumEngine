import pygame as pg

from game.block import Block


class StoneBlock(Block):

    @classmethod
    def preload(cls):
        cls.tile = pg.image.load("resources/textures/blocks/stone.png").convert()


Block.register("std:stone", StoneBlock)
