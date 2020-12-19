from .entity import Entity


class InvalidEntity(Entity):
    
    @classmethod
    def from_save(cls, save):
        return cls(save)
    
    def update(self, dtime):
        pass

    def __init__(self, save):
        self.save = save

    def on_save(self):
        return self.save['data']
    
    def get_position(self):
        return self.data['position']
    
    def get_velocity(self):
        return self.data['velocity']
