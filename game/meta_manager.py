import uuid
import json

from utils.weakobj import WeakObject


class MetaManager:
    instance = None
    
    @classmethod
    def load(cls, fn):
        data = {}

        cls._savename = fn

        try:
            file = open(fn)
            
            data = json.load(file)
            
            file.close()
        except FileNotFoundError:
            pass
        
        cls.instance = cls(data)
        return WeakObject(cls.instance)

    @classmethod
    def get(cls):
        return WeakObject(cls.instance)

    def __init__(self, data=None):
        self.data = data or {}

    def newmeta(self, key=None):
        if key is None:
            key = str(uuid.uuid1())

        self.data[key] = {}
        
        return key, self.data[key]

    def delmeta(self, key):
        if self.data.get(key):
            del self.data[key]

    def getmeta(self, key):
        return self.data.get(key)
    
    def save(self, fn):
        file = open(fn, 'w')
        
        json.dump(self.data, file, indent=4)
        
        file.close()
