#!/usr/bin/python3

import itertools

CURRENT_VERSION = 1


def encode(foreground, midground, background, blocksize):
    """Encode world data for saving in binary file

    foreground, midground, and background - 2d arrays of block sidentifiers
    blocksize - size of block identifier (bytes)

    Returns bytes"""
    
    HEADERSIZE = 10

    width = len(foreground[0])
    height = len(foreground)
    # width and height for fg, mg, and bg are equal
    
    result = memoryview(bytearray(HEADERSIZE + width*height*3*blocksize))

    result[0:1] = CURRENT_VERSION.to_bytes(1, 'little')  # File format version

    result[1:5] = width.to_bytes(4, 'little')
    result[5:9] = height.to_bytes(4, 'little')

    result[9:10] =  blocksize.to_bytes(1, 'little')  # Bytes per block
    
    cells = 0

    for y in range(height):
        for x in range(width):
            pos = HEADERSIZE + (y*width*3+x*3)
            result[pos:(pos+blocksize)] = foreground[y][x].to_bytes(blocksize, 'little')

            pos += blocksize
            result[pos:(pos+blocksize)] = midground[y][x].to_bytes(blocksize, 'little')
            
            pos += blocksize
            result[pos:(pos+blocksize)] = background[y][x].to_bytes(blocksize, 'little')
            
            cells += 1
    
    print(f"Wrote {cells} cells of world {width}x{height}")

    return result.tobytes()


def decode(data):
    """Decode world data from bytes

    Returns tuple of 3 2d arrays of block identifiers"""
    mv = memoryview(data)
    
    version = mv[0]
    
    if version != CURRENT_VERSION:
        raise ValueError(f"Unsupported world file version - {version} "
                         "(is this actually a world file?)")

    width = int.from_bytes(mv[1:5], 'little')
    height = int.from_bytes(mv[5:9], 'little')

    blocksize = mv[9]

    world = mv[10:]

    if len(world) != width*height*blocksize*3:  # 3 - three layers
                                                # fg, mg, and bg
        raise ValueError(
            f"wrong world size ({width*height*blocksize*3} bytes "
            f"expected, got {len(world)})")

    foreground = []
    midground = []
    background = []
    read = 0

    for i in range(height):
        line = world[width*i*3:width*(i+1)*3]

        fg_line = []
        mg_line = []
        bg_line = []

        if not line:
            continue

        for j in range(0, width*3, 3):
            fg_line.append(
                int.from_bytes(
                    line[j*blocksize:j*blocksize+blocksize], 'little'))
            mg_line.append(
                int.from_bytes(
                    line[(j+1)*blocksize:(j+1)*blocksize+blocksize], 'little'))
            bg_line.append(
                int.from_bytes(
                    line[(j+2)*blocksize:(j+2)*blocksize+blocksize], 'little'))
            read += 1

        foreground.append(fg_line)
        midground.append(mg_line)
        background.append(bg_line)
    
    print(f"Read {read} cells from world {width}x{height}")

    return (foreground, midground, background)


def show(filename):
    '''
    file-like utility that prints information about terrarium file
    
    Supported versions: 1
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
