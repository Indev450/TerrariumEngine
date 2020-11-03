#!/usr/bin/python3

def encode(blocks, blocksize):
    """Encode world data for saving in binary file

    blocks - 2d array of block identifiers
    blocksize - size of block identifier

    Returns bytes"""

    out = b''

    out += len(blocks[0]).to_bytes(4, 'little')  # Width
    out += len(blocks).to_bytes(4, 'little')  # Height

    out += blocksize.to_bytes(1, 'little')

    for line in blocks:
        for block in line:
            out += block.to_bytes(blocksize, 'little')

    return out


def decode(data):
    """Decode world data from bytes

    Returns 2d array of block identifiers"""
    mv = memoryview(data)

    width = int.from_bytes(mv[:4], 'little')
    height = int.from_bytes(mv[4:8], 'little')

    blocksize = mv[8]

    world = mv[9:]

    if len(world) != width*height*blocksize:
        raise ValueError(
            f"wrong world size ({width*height*blocksize} "
            f"expected, got {len(world)})")

    result = []

    for i in range(height):
        line = world[width*i:width*(i+1)]
        resultline = []

        if not line:
            break

        for j in range(width):
            resultline.append(
                int.from_bytes(
                    line[j*blocksize:j*blocksize+blocksize], 'little'))

        result.append(resultline)

    return result


def show(filename):
    file = None
    
    try:
        file = open(filename, 'rb')
    except FileNotFoundError:
        print(f"{filename}: no such file or directory")
    else:
        mv = memoryview(file.read())
        
        width = int.from_bytes(mv[:4], 'little')
        height = int.from_bytes(mv[4:8], 'little')

        blocksize = mv[8]
        
        print(f'{filename}: Terrarium world, {width}x{height} blocks, {blocksize} bytes per block')


def main():
    import sys

    if len(sys.argv) < 2:
        print('Not enought arguments')
    else:
        filename = sys.argv[1]
        show(filename)


if __name__ == "__main__":
    main()
