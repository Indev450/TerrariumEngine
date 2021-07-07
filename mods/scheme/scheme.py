from game.block import BlockDefHolder


def read_scheme(file):
    """Read scheme from file object. This function must be run only
    when BlockDefHolder.init_int_ids called, because it calls id_by_strid"""
    scheme = {
        'width': 0,
        'height': 0,
        'foreground': [],
        'midground': [],
        'background': [],
    }
    
    layer = 'foreground'
    
    blocks = {
        'foreground': {
            ' ': 0,
            '\\': -1,
        },
        'midground': {
            ' ': 0,
            '\\': -1,
        },
        'background': {
            ' ': 0,
            '\\': -1,
        },
    }
    
    width = 0
    
    add_lines = False
    
    while True:
        data = file.readline()
        
        if not data:
            break
        
        data = data.strip()
        
        if data.startswith('!'):
            cmd, *args = data[1:].split()
            
            if cmd == 'layer':
                if not args:
                    raise ValueError('command "layer" requires an argument')
                
                layer = args[0]
                
                if layer not in ('foreground', 'midground', 'background'):
                    raise ValueError(f'unknown layer "{layer}"')
            
            elif cmd == 'block':
                if len(args) != 3:
                    raise ValueError('command "block" requires 3 arguments')
                
                layer, strid, alias = args
                
                if layer not in ('foreground', 'midground', 'background'):
                    raise ValueError(f'unknown layer "{layer}"')
                
                blocks[layer][alias] = BlockDefHolder.id_by_strid(strid)
            
            elif cmd == 'begin':
                add_lines = True
            
            elif cmd == 'end':
                add_lines = False
            
            elif cmd == 'space':
                if not args:
                    raise ValueError('command "layer" requires an argument')
                
                count = int(args[0])
                
                scheme[layer].append(' '*count)
            
            else:
                raise ValueError(f'unknown command: {cmd}')
            
        elif add_lines:
            if len(data) > width:
                width = len(data)
            scheme[layer].append(data)
    
    scheme['height'] = max((len(scheme['foreground']),
                            len(scheme['midground']),
                            len(scheme['background'])))

    return blocks, scheme


def place_scheme_mg(mapgen, x, y, blocks, scheme):
    for layer in ('foreground', 'midground', 'background'):
        put = getattr(mapgen, f'put_{layer}')
        
        yoff = 0
        
        for line in scheme[layer]:
            xoff = 0
            
            for c in line:
                block = blocks[layer][c]
                
                if block != -1:
                    put(x + xoff, y + yoff, block)
                
                xoff += 1
            
            yoff += 1


def scheme_from_world(world, x1, y1, x2, y2):
    raise NotImplementedError
    
    scheme = {
        'foreground': [],
        'midground': [],
        'background': [],
    }
    
    blocks = {
        'foreground': {
            ' ': 0,
        },
        'midground': {
            ' ': 0,
        },
        'background': {
            ' ': 0,
        },
    }
    
    aliases = {
        'foreground': {
            0: ' ',
        },
        'midground': {
            0: ' ',
        },
        'background': {
            0: ' ',
        },
    }
    
    for y in range(y1, y2+1):
        line = []
        
        for x in range(x1, x2+1):
            pass
