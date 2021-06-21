#!/usr/bin/env python

import argparse

import pygame as pg

try:
    from PIL import Image
except ImportError:
    Image = None


flags = {
    'up': 0b1000,
    'down': 0b0100,
    'left': 0b0010,
    'right': 0b0001,
}

tilemap_positions = {
    0: (0, 0),  # No neighbours
    flags['up'] : (1, 0),  # Upper neighbour
    flags['up'] | flags['down']: (2, 0),  # Upper & down neighbours
    flags['up'] | flags['left']: (3, 0),  # Upper & left neighbours
    flags['up'] | flags['right']: (4, 0),  # Upper & right neighbours
    flags['up'] | flags['down'] | flags['left']: (5, 0),  # Upper, down & left neighbours
    flags['up'] | flags['down'] | flags['right']: (6, 0),  # Upper, down & right neighbours
    15: (7, 0),  # All neighbours
    flags['down'] | flags['left']: (0, 1),  # Down & left neighbour
    flags['down'] | flags['right']: (1, 1),  # Down & right neighbour
    flags['down'] | flags['left'] | flags['right']: (2, 1),  # Down, right & left neighbours
    flags['left'] | flags['right']: (3, 1),  # Left & right neighbour'
    flags['left']: (4, 1),  # Left neighbour
    flags['right']: (5, 1),  # Right neighbour
    flags['down']: (6, 1),  # Down neighbour
    flags['up'] | flags['left'] | flags['right']: (7, 1),  # Upper, left and right neighbours
}


def make_tile_map(block, side, output, delcolor=None):
    blocktex = pg.image.load(block)
    
    sidetex_up = pg.image.load(side)
    sidetex_down = pg.transform.rotate(sidetex_up, 180)
    sidetex_left = pg.transform.rotate(sidetex_up, 90)
    sidetex_right = pg.transform.rotate(sidetex_up, -90)
    
    tilemap = pg.Surface((128, 32), pg.SRCALPHA)
    
    for key in tilemap_positions.keys():
        pos = tilemap_positions[key]
        pos = pos[0]*16, pos[1]*16
        
        tilemap.blit(blocktex, pos)
        
        if key & flags['up']:
            tilemap.blit(sidetex_up, pos)
        if key & flags['down']:
            tilemap.blit(sidetex_down, pos)
        if key & flags['left']:
            tilemap.blit(sidetex_left, pos)
        if key & flags['right']:
            tilemap.blit(sidetex_right, pos)
    
    if delcolor is not None:
        delcolor = pg.Color(delcolor)
        for x in range(128):
            for y in range(32):
                if tilemap.get_at((x, y)) == delcolor:
                    tilemap.set_at((x, y), pg.Color('#00000000'))
    
    file = open(output, 'wb')
    
    data = pg.image.tostring(tilemap, 'RGBA')
    
    img = Image.frombuffer('RGBA', (128, 32), data)
    
    img.save(file, 'PNG')
    
    file.close()


def main():
    if Image is None:
        raise SystemExit("Error: this script requires PIL (try python -m pip install pillow)")
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--block', metavar='block', help='Block background')
    parser.add_argument('--side', metavar='side', help='Block side')
    parser.add_argument('--output', metavar='output', help='Output file')
    parser.add_argument('--delcolor', metavar='delcolor', help='That color will be removed from result', default=None)
    
    args = parser.parse_args()
    
    make_tile_map(args.block, args.side, args.output, args.delcolor)


if __name__ == '__main__':
    main()
