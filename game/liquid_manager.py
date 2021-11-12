# Stuppid cirlular imports
import game.block as b

from game.game_object import GameObject


class Liquid(GameObject):
    
    def __init__(self, x, y, type, level=5):
        super().__init__(x, y, b.Block.WIDTH, b.Block.HEIGHT)
        
        self.type = type
        self.image = type.TEXTURE
        self.id = type.ID
        
        self.level = level
    
    def draw(self, screen):
        if self.level < 1 or self.level > 5:
            return
        
        self.image.select(x=self.level-1, y=0)
        
        super().draw(screen)


class LiquidDef:
    ID = 'builtin:liquid'
    
    TEXTURE = None  # Should be TiledTexture with 5 horizontal tiles
                    # for each liquid level, starting from minimal
    
    UPDATE_TIME = 1  # Update liquid every UPDATE_TIME seconds
    
    DAMAGE = 0  # How much damage will any entity take every second beeing in this
                # liquid?
    
    DAMAGE_TYPE = ""  # What type of damage this liquid have? ("lava" for example)
    
    RESISTANCE = 0.7  # Entity's speed in liquid will be multiplied at this value
    
    @classmethod
    def register(cls):
        Liquids.registered[cls.ID] = cls


class Liquids:
    registered = {}


class LiquidManager:
    
    def __init__(self, world):
        # I really hate circular imports
        from utils.items import do_cooldown
        
        self.world = world
        
        self.liquids = {}
        self.update_time = {}
        
        for liquid in Liquids.registered.values():
            self.update_time[liquid.ID] = do_cooldown(liquid.UPDATE_TIME)
    
    def add_liquid(self, x, y, id, level=5):
        x = int(x)
        y = int(y)
        
        if self.liquids.get((x, y)) is None:
            self.liquids[(x, y)] = Liquid(
                x*b.Block.WIDTH, y*b.Block.HEIGHT,
                type=Liquids.registered.get(id),
                level=level,
            )
    
    def update(self, section, dtime):
        need_update = []
        
        for liquid in self.update_time.keys():
            if self.update_time[liquid](liquid):
                need_update.append(liquid)
        
        for x in range(section.left, section.right):
            for y in range(section.bottom, section.top, -1):
                src = (x, y)
                
                if self.liquids.get(src) is None:
                    continue
                
                if self.liquids[src].level < 1:
                    del self.liquids[src]
                    continue
                
                liquid = self.liquids[src]
                
                if liquid.id not in need_update:
                    continue
                
                dst = (src[0], src[1] + 1)
                
                if self.world.get_fg_block(*dst) is None:
                    if self.try_merge(src, dst):
                        continue
                
                dst = (src[0] + 1, src[1])
                
                if self.world.get_fg_block(*dst) is None:
                    if self.try_merge(src, dst):
                        pass
                
                dst = (src[0] - 1, src[1])
                
                if self.world.get_fg_block(*dst) is None:
                    if self.try_merge(src, dst):
                        pass
    
    def draw(self, section, screen):
        for x in range(section.left, section.right):
            for y in range(section.top, section.bottom):
                l = self.liquids.get((x, y))
                
                if l is not None:
                    l.draw(screen)
    
    def try_merge(self, pos_from, pos_into):
        horizontal = pos_from[1] == pos_into[1]
        
        src = self.liquids[pos_from]
        
        dst = self.liquids.get(pos_into)
        
        if dst is None:
            dst = Liquid(pos_into[0]*b.Block.WIDTH, pos_into[1]*b.Block.HEIGHT,
                         type=src.type, level=0)
            
            self.liquids[pos_into] = dst
        
        self.liquids[pos_into] = dst  # In case if there was no liquid
        
        if src.id != dst.id or dst.level == 5: return False
        
        if not horizontal:
            dst.level += src.level
            
            if dst.level > 5:
                src.level = dst.level - 5
                dst.level = 5
                
                return False
            
            else:
                del self.liquids[pos_from]

                return True
        
        else:
            diff = max(abs(src.level - dst.level)//2, 1)
            
            if dst.level > src.level:
                dst.level -= diff
                src.level += diff
            
            elif src.level > dst.level:
                src.level -= diff
                dst.level += diff
            
            return src.level != 0
    
    def serialize(self):
        # Yes, i know that concatenating a lot of bytes is slow, but for now
        # i dont know how to do it better 
        result = b''
        
        # First, separe all liquids by type
        liquids = {}
        
        for pos, liquid in self.liquids.items():
            if liquids.get(liquid.id) is None:
                liquids[liquid.id] = []
            
            liquids[liquid.id].append((pos, liquid.level))
        
        for liquid_id, liquid_list in liquids.items():
            name = liquid_id.encode()
            result += len(name).to_bytes(1, 'little')
            result += name
            result += len(liquid_list).to_bytes(4, 'little')
            
            for liquid in liquid_list:
                serialized = memoryview(bytearray(1+4+4))  # level, x, y
                serialized[0:1] = liquid[1].to_bytes(1, 'little')
                serialized[1:5] = liquid[0][0].to_bytes(4, 'little')
                serialized[5:9] = liquid[0][1].to_bytes(4, 'little')
                
                result += serialized

        return result
    
    def deserialize(self, data):
        data = memoryview(bytearray(data))
        
        pos = 0
        
        while pos < len(data):
            id_size = data[pos]
            pos += 1
            
            liquid_id = data[pos:pos+id_size].tobytes().decode()
            pos += id_size
            
            count = int.from_bytes(data[pos:pos+4], 'little')
            pos += 4
            
            for i in range(count):
                level = data[pos]
                pos += 1
                
                x = int.from_bytes(data[pos:pos+4], 'little')
                pos += 4
                
                y = int.from_bytes(data[pos:pos+4], 'little')
                pos += 4
                
                self.add_liquid(x, y, liquid_id, level)
