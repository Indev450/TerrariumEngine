from game.block import Block

from worldfile.worldfile import encode


class Mapgen:

    def __init__(self, mods, output, width, height):
        Block.sort_registered_entries()

        self.mods = mods

        self.ofile = open(output, 'wb')

        self.width = width
        self.height = height

        self.blocks = [[0 for i in range(self.width)] for i in range(self.height)]

    def save(self):
        blocksize = int(Block.registered_count()/256) + 1
        data = encode(self.blocks, blocksize)
        self.ofile.write(data)
        self.ofile.close()

    def run(self):
        pass
