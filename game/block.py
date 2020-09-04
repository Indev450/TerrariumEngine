import pygame as pg

from .game_object import GameObject


class Block(GameObject):
    WIDTH = 32
    HEIGHT = 32

    registered_blocks = {"std:air": {
        "entry": None,
        "id": 0,
    }}
    _registered_blocks = []  # int ids for registered entries
                                 # None - air block

    tile = None

    ID = 0

    def __init__(self, *position):
        super().__init__(*position, self.WIDTH, self.HEIGHT)

    def init_graphics(self, width, height):
        self.image = self.get_tile()

    def getid(self):
        return self.id

    @classmethod
    def preload(self):
        pass

    @classmethod
    def get_tile(cls):
        return cls.tile

    @classmethod
    def by_id(cls, id):
        try:
            return cls._registered_blocks[id]
        except IndexError:
            pass

    @classmethod
    def id_by_strid(cls, strid):
        return cls.registered_blocks[strid]["id"]

    @classmethod
    def by_idstr(cls, idstr):
        block = cls.registered_blocks.get(idstr)
        if block is not None:
            return block["entry"]

    @classmethod
    def register(cls, idstr, block_type):
        cls.registered_blocks[idstr] = {
            "entry": block_type,
            "id": None,
        }

    @classmethod
    def on_preload(cls):
        for block in cls.registered_blocks.values():
            if block["entry"] is not None:
                block["entry"].preload()

        cls.sort_registered_entries()

    @classmethod
    def registered_count(cls):
        return len(cls._registered_blocks)

    @classmethod
    def sort_registered_entries(cls):
        cls._registered_blocks = [None]

        keys = list(cls.registered_blocks.keys())
        keys.sort()

        for i in range(1, len(keys)):
            cls._registered_blocks.append(cls.registered_blocks[keys[i]]["entry"])
            cls.registered_blocks[keys[i]]['id'] = i
            cls._registered_blocks[i].ID = i
