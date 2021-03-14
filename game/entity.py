import traceback

from .world import World
from .game_object import GameObject

from config import getcfg


config = getcfg()


class Entity(GameObject):
    registered = {}
    ID = ''
    
    GRAVITY = config["entity.default.gravity"]  # Fall speed
    BRAKING = config["entity.default.braking"]  # To avoid endless motion of object
    MIN_SPEED = config["entity.default.min_speed"]  # Minimum horizontal speed
    MAX_SPEED = config["entity.default.max_speed"]  # Maximum horizontal speed
    MAX_FALL = config["entity.default.max_fall"]  # Maximum of fall speed
    
    @classmethod
    def register(cls):
        if cls.registered.get(cls.ID) is not None:
            traceback.print_stack()
            print(f'Warning: entity {cls.ID} already registered')
        cls.registered[cls.ID] = cls
    
    @classmethod
    def get(cls, key):
        return cls.registered.get(key)

    @classmethod
    def from_save(cls, manager, uuid, save):
        return cls(manager,
                   uuid,
                   position=save['entity']['position'],
                   velocity=save['entity']['velocity'])

    def __init__(self,
                 manager=None,
                 uuid=None,
                 position=(0, 0),
                 velocity=(0, 0),
                 size=(10, 10)):
        super().__init__(*position, *size)

        self.xv, self.yv = velocity

        self.friction = 20

        self.on_ground = False
        
        self.ignore_collision = False

        self.world = World.get()
        
        self.manager = manager
        
        self.uuid = uuid
        
        self.tags = []  # All tags added to entity
    
    def assign_to_manager(self, manager):
        self.manager = manager

    def update(self, dtime):
        """Called every frame. Updates entitys physics"""
        acceleration = self.xv - self.xv*self.BRAKING

        
        if not (self.xv > self.MAX_SPEED or self.xv < -self.MAX_SPEED):
            self.xv -= acceleration * dtime * self.friction

        if abs(self.xv) < self.MIN_SPEED:
            self.xv = 0

        if not self.on_ground:
            self.yv += self.GRAVITY * dtime

            if self.yv < self.MAX_FALL:
                self.yv = self.MAX_FALL

        self.on_ground = False
        self.rect.y += self.yv
        
        if not self.ignore_collision:
            self.collide(False)

        self.rect.x += self.xv
        
        if not self.ignore_collision:
            self.collide(True)
    
    def collide(self, by_x):
        """Checks collision for one dimension"""
        self.world.is_collide(
            self,
            self._on_collide_x if by_x else self._on_collide_y)
    
    def on_save(self):
        """Called when game saves. Can be used to save
        some meta, or self. Should return json-supporting
        object or None"""
        pass
    
    def get_velocity(self):
        return self.xv, self.yv
    
    def add_tag(self, tag):
        if self.manager is None:
            print('Error: cannot tag entity without manager')
            return
        
        self.manager.tag_entity(self, tag)
        self.tags.append(tag)
    
    def del_tag(self, tag):
        if self.manager is None:
            print('Error: cannot untag entity without manager')
            return
            
        if tag not in self.tags:
            print(f'Warning: entity has no such tag: {tag}')
        
        self.manager.untag_entity(self, tag)
        self.tags.remove(tag)
    
    def on_deleted(self):
        if self.manager is None:
            print('Error: cannot do default cleanup without manager')
            return

        for tag in self.tags:
            self.manager.untag_entity(self, tag)

    def _on_collide_x(self, block):
        """Collide callback for x"""
        if self.xv > 0:
            self.rect.right = block.rect.left
            self.xv = 0

        if self.xv < 0:
            self.rect.left = block.rect.right
            self.xv = 0

    def _on_collide_y(self, block):
        """Collide callback for y"""
        if self.yv > 0:
            self.rect.bottom = block.rect.top
            self.on_ground = True
            self.yv = 0

        if self.yv < 0:
            self.rect.top = block.rect.bottom
            self.yv = 0
