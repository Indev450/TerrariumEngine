from .game_object import GameObject


class DecorationManager:
    instance = None
    
    @classmethod
    def new(cls):
        cls.instance = cls()
        return cls.instance
    
    @classmethod
    def get(cls):
        return cls.instance
    
    def __init__(self):
        self.decorations = []
    
    def add(self, decor):
        self.decorations.append(decor)
    
    def remove(self, decor):
        try:
            self.decorations.remove(decor)
        except ValueError:
            print(f'Error: DecorationManager.remove(): decoration not found')
    
    def update(self, dtime):
        for decor in self.decorations:
            decor.update(dtime)
            
            if decor.to_remove:
                self.decorations.remove(decor)
    
    def draw(self, screen):
        for decor in self.decorations:
            decor.draw(screen)


class Decor(GameObject):
    texture = None
    
    max_lifetime = None
    
    SIZE = (16, 16)
    
    def __init__(self, manager, x, y):
        super().__init__(x, y, *self.SIZE)
        
        self.manager = manager
        
        self.lifetime  = 0
        
        self.to_remove = False
        
        self.image = self.texture
        
    def update(self, dtime):
        self.lifetime += dtime
        
        if self.max_lifetime is not None and self.lifetime >= self.max_lifetime:
            self.to_remove = True
            return
        
        self.update_position()

    def update_position(self):
        pass
