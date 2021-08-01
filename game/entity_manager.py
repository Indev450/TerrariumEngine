import uuid
import json

from .entity import Entity
from .invalid_entity import InvalidEntity

from utils.weakobj import WeakObject


class EntityManager:
    instance = None
    
    def load(self, fn):
        self.tags = {}  # Clear tags
        
        _data = {}

        try:
            file = open(fn)
            
            _data = json.load(file)
            
            file.close()
        except FileNotFoundError:
            pass
        
        data = {}
        
        for key in _data.keys():
            entsave = _data[key]
            
            entcls = Entity.get(entsave['entity']['id'])
            
            if entcls is None:
                print(f"Error: could not load entity {entsave['entity']['id']}: "
                      "type of entity not known (keeping as InvalidEntity)")
                entcls = InvalidEntity
                # If mod that adds this entity was deleted we will keep entity

            data[key] = entcls.from_save(WeakObject(self), key, entsave)
        
        self.data = data

    @classmethod
    def get(cls):
        return WeakObject(cls.instance)
    
    @classmethod
    def new(cls):
        cls.instance = cls()
        return WeakObject(cls.instance)
    
    def __init__(self, data=None):
        self.data = data or {}
        self.tags = {}
    
    def tag_entity(self, entity, tag):
        if self.tags.get(tag) is None:
            self.tags[tag] = []
        
        if entity.uuid in self.tags[tag]:
            return
        
        self.tags[tag].append(entity.uuid)
    
    def untag_entity(self, entity, tag):
        if not self.tags.get(tag):
            return
        
        try:
            self.tags[tag].remove(entity.uuid)
        except ValueError:
            print(f'Warning: cannot untag entity: entity has no tag {tag}')
    
    def get_tagged_entities(self, tag):
        entities = []
        
        for id in self.tags.get(tag, []):
            entity = self.data.get(id)
            
            if entity is not None:
                entities.append(entity)
        
        return entities
    
    def newentity(self, id, key, *args, **kwargs):
        if key is None:
            key = str(uuid.uuid1())
        
        ent = Entity.get(id)(manager=WeakObject(self), uuid=key, *args, **kwargs)
        
        self.data[key] = ent
        
        return (WeakObject(ent), key)

    def delentity(self, key):
        if self.data.get(key):
            self.data[key].on_deleted()
            del self.data[key]

    def getentity(self, key):
        return WeakObject(self.data.get(key))
    
    def update(self, dtime):
        for ent in list(self.data.values()):
            ent.update(dtime)

    def draw(self, screen):
        for ent in self.data.values():
            ent.draw(screen)
    
    def save(self, fn):
        file = open(fn, 'w')

        data = {}
        
        for key in self.data.keys():
            entity = self.data[key]
            
            entdata = entity.on_save()
    
            if entdata is not None:
                data[key] = {
                    'data': entdata,
                    'entity': {
                        'id': entity.ID,
                        'position': entity.get_position(),
                        'velocity': entity.get_velocity(),
                    }
                }
        
        json.dump(data, file,
                  default=lambda obj: print(f'Error: could not save entity (data={obj})'),
                  indent=4)
        # default replaces non-serializable objects with null
        # to not corrupt data

        file.close()
