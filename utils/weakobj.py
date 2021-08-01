import weakref


class WeakObject:
    """Same as weakref object, but you don't need to call it"""
    
    def __init__(self, obj):
        self.obj = weakref.ref(obj)
    
    def __getattribute__(self, name):
        if name == 'obj':
            return super().__getattribute__(name)
        return getattr(super().__getattribute__('obj')(), name)
    
    def __setattr__(self, name, value):
        if name == 'obj':
            super().__setattr__(name, value)
            return
        setattr(super().__getattribute__('obj')(), name, value)

    def __hash__(self):
        return hash(self.obj())
    
    def __eq__(self, other):
        return self.obj() is other.obj()
    
    def __bool__(self):
        return self.obj() is not None
    
    def exists(self):
        return bool(self)
