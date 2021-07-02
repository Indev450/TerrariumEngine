from random import randint

from game.item import Item
from game.block import BlockDefHolder, Block

from .chest import Chest


def box_dungeon(mapgen):
    '''Single box containing a chest with random loot'''
    for i in range(mapgen.width*mapgen.height//10000):
        x, y = randint(0, mapgen.width - 9), randint(mapgen.height//3, mapgen.height - 10)
        
        generate_dungeon(mapgen, x, y)


def generate_dungeon(mapgen, startx, starty):
    stone = BlockDefHolder.id_by_strid('std:stone')
    
    for x in range(startx, startx+9):
        for y in range(starty, starty+10):
            if x in (startx, startx+8) or y in (starty, starty+9):
                mapgen.put_foreground(x, y, stone)
            else:
                mapgen.put_foreground(x, y, 0)
    
    x = startx + 4
    y = starty + 8
    
    if mapgen.get_foreground(x, y) != 0 or mapgen.get_midground(x, y) != 0 or mapgen.get_foreground(x, y+1) == 0:
        return

    mapgen.put_midground(x, y, 1)
    chest, _ = mapgen.entity_manager.newentity("std:chest", None, position=(x*Block.WIDTH, y*Block.HEIGHT))
    
    for i in range(randint(2, 5)):
        chest.inventory.set_item(
            'main', randint(0, 8*4-1), 
            Item.get('std:stone') if randint(1, 5) < 4 else Item.get('std:copper_ore'), randint(4, 10))
