#!/usr/bin/python3

import itertools
import array


CURRENT_VERSION = 2


def encode(worldarr, width, height):
    """Encode world data for saving in binary file

    Returns bytes"""
    
    HEADERSIZE = 9
    
    result = memoryview(bytearray(HEADERSIZE + width*height*3*worldarr.itemsize))

    result[0:1] = CURRENT_VERSION.to_bytes(1, 'little')  # File format version

    result[1:5] = width.to_bytes(4, 'little')
    result[5:9] = height.to_bytes(4, 'little')
    
    result[9:] = worldarr.tobytes()

    return result.tobytes()


def decode(data):
    """Decode world data from bytes

    Returns world data and size of world"""
    mv = memoryview(bytearray(data))
    
    version = mv[0]
    
    if version != CURRENT_VERSION:
        raise ValueError(f"Unsupported world file version - {version} "
                         "(is this actually a world file?)")

    width = int.from_bytes(mv[1:5], 'little')
    height = int.from_bytes(mv[5:9], 'little')

    world = mv[9:]
    
    worldarr = array.array('I')
    worldarr.frombytes(world)
    
    assert len(worldarr) == width*height*3, 'size of loaded world not equals size in header'

    return (worldarr, width, height)


def show(filename):
    '''
    file-like utility that prints information about terrarium file
    
    Supported versions: 1, 2
    
    Version changelog:
        Version 2:
            Now blocksize is c_uint size and this field was removed
            from header, since array.array used for storing blocks.
            However, that can bring difficulities when sharing map with
            someone who has different c_uint size.
            TODO - make converter between maps with different
    '''
    file = None
    
    try:
        file = open(filename, 'rb')
    except FileNotFoundError:
        print(f"{filename}: no such file or directory")
    except IsADirectoryError:
        print(f"{filename}: is a directory")
    else:
        mv = memoryview(file.read())
        
        version = mv[0]

        if version == 1:
            width = int.from_bytes(mv[1:5], 'little')
            height = int.from_bytes(mv[5:9], 'little')

            blocksize = mv[9]
        
            print(f'{filename}: Terrarium world version {version}, '
                  f'{width}x{height} blocks, {blocksize} bytes per '
                   'block (3 layers)')
        elif version == 2:
            width = int.from_bytes(mv[1:5], 'little')
            height = int.from_bytes(mv[5:9], 'little')
        
            print(f'{filename}: Terrarium world version {version}, '
                  f'{width}x{height} blocks, 4 bytes per '
                   'block (3 layers)')
        else:
            print(f'{filename}: unsupported world version: {version} '
                  '(is this actually a Terrarium world?)')


def main():
    import sys

    if len(sys.argv) < 2:
        print('Not enought arguments')
    elif len(sys.argv) > 2:
        print('Too many arguments')
    else:
        filename = sys.argv[1]
        if (filename.endswith('.tworld') or
            filename.endswith('.tcworld')):  # Old file extension
            show(filename)
        else:
            print(f'{filename}: not a Terrarium world')


if __name__ == "__main__":
    main()
