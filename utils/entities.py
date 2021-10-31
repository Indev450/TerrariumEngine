import random

from game.entity_manager import EntityManager
from game.world import World

from config import getcfg


config = getcfg()


class Spawner:
    '''Object that spawns entity when called'''
    MAXENTITIES = 8
    
    def __init__(self):
        self.spawned = []
        
    def __call__(self):
        if len(self.spawned) >= self.MAXENTITIES:
            if not self.check():
                return
        
        entmanager = EntityManager.get()
        
        if not entmanager:
            return
        
        for player in entmanager.get_tagged_entities('player'):
            x, y = player.get_position()
            
            offx, offy = random.randint(-20, 20), random.randint(-20, 20)
            
            offx = offx + (config['app.resolution'][0] if offx > 0 else -config['app.resolution'][0])
            offy = offy + (config['app.resolution'][1] if offy > 0 else -config['app.resolution'][1])

            x += offx
            y += offy
            
            if self.can_spawn(x, y):
                key = self.spawn(entmanager, x, y)
                
                if key is not None:
                    self.spawned.append(key)
    
    def check(self):
        '''Checks is spawned entities still exists.
        Returns true if some of entiies were deleted.'''
        manager = EntityManager.get()
        to_remove = []
        
        for uuid in self.spawned:
            if manager.getentity(uuid) is None:
                to_remove.append(uuid)
        
        for uuid in to_remove:
            self.spawned.remove(uuid)
        
        return len(to_remove) != 0
    
    def can_spawn(self, x, y):
        '''Checks for some spawn conditions.'''
        return False
    
    def spawn(self, entmanager, x, y):
        '''Should spawn entity at given position and return its uuid
        or None on fail'''
        pass
    
    def add_spawn_tick(self, ticks=10):
        '''Add tick event to the ticker if it possible. Returns True on success'''
        world = World.get()
        
        if world is None:
            return False
        
        world.ticker.add_timer(ticks, self, True)
        
        return True
