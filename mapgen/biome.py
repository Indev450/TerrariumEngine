class Biome:
    id = 'builtin:biome_base'
    name = 'Biome'
    
    def __init__(self, mapgen):
        self.mapgen = mapgen
        # Reference to mapgen object
        
        self.overnoise = None
        # Noise that 'lays' on the original one
        # Not used if None
        # Noise should be callable object with 2 arguments for position

        self.overnoise_scale_x = 100.0
        self.overnoise_scale_y = 100.0
        # Scale for 'overnoise'
    
    def get_bounds(self, world_width, world_height):
        '''Get bounds of biome. Bounds are:
        ((left, top), (right, bottom))'''
        return (0, 0, 0, 0)

    def get_blocks(self, value, blocks):
        '''Should return tuple of 3 integer block ids
        value - noise value
        blocks - blocks which already placed on this position
        Given and returned tuples of blocks are:
        (foreground, midground, background)'''
        return blocks

    def get_blocks_at(self, x, y, orignoise, blocks):
        '''Get block at given position.
        orignoise - noise value
        blocks - blocks which already placed on this position
        Given and returned tuples of blocks are:
        (foreground, midground, background)'''
        overnoise = 0
        
        if self.overnoise is not None:
            overnoise = self.overnoise(
                x/self.overnoise_scale_x,
                y/self.overnoise_scale_y)
        
        return self.get_blocks(
                (orignoise+overnoise) / (2 if self.overnoise else 1),
                blocks)
