from .texture import gettransparent

from .block import Block
from .entity import Entity
from .entity_manager import EntityManager


def interactive(cls):
    class InteractiveEntity(Entity):
        ID = f'{cls.id}_entity'
        
        def __init__(self,
                     manager=None,
                     uuid=None,
                     position=(0, 0)):
            super().__init__(manager=manager,
                             uuid=uuid,
                             position=position,
                             velocity=(0, 0),
                             size=(Block.WIDTH, Block.HEIGHT))

            self.image = cls.tile
            
            self.block = (position[0]//Block.WIDTH, position[1]//Block.HEIGHT)
            self.checkblock = (self.block[0], self.block[1] + 1)
            
            self.add_tag('interactive')
        
        def on_interact(self, player):
            cls.on_interact(player)
        
        
        def update(self, dtime):
            if (self.world.get_fg_block(*self.checkblock) is None
                and self.world.get_mg_block(*self.checkblock) is None):
                self.world.set_mg_block(*self.block, 0)
    
    
    class InteractiveBlock(cls):
        loaded = {}
        
        _entmgr = None
        
        tile = gettransparent(1, 1)
        
        @classmethod
        def on_load(cls, x, y):
            super().on_load(x, y)
            
            cls.add_block_entity(x, y)
        
        @classmethod
        def on_place(cls, x, y):
            super().on_place(x, y)
            
            cls.add_block_entity(x, y)
        
        @classmethod
        def on_destroy(cls, x, y):
            super().on_destroy(x, y)
            
            manager = EntityManager.get()
            
            if cls._entmgr is not manager:
                cls._entmgr = manager
                cls.loaded = {}
            
            uuid = cls.loaded.get((x, y))
            
            if uuid is not None:
                manager.delentity(uuid)
        
        @classmethod
        def add_block_entity(cls, x, y):
            manager = EntityManager.get()
            
            if cls._entmgr is not manager:
                cls._entmgr = manager
                cls.loaded = {}
            
            if cls.loaded.get((x, y)) is None:
                _, cls.loaded[(x, y)] = manager.newentity(
                    f'{cls.id}_entity', None,
                    position=(Block.WIDTH*x, Block.HEIGHT*y))
        
        @classmethod
        def register(cls):
            super().register()
            InteractiveEntity.register()
    
    return InteractiveBlock
