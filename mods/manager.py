import os
import importlib
import traceback


class ModManager:
    instance = None
    
    curmodpath = ''
    
    @classmethod
    def get(cls):
        if cls.instance is None:
            cls.instance = cls()
        
        return cls.instance
    
    @classmethod
    def _set_modpath(cls, path):
        cls.curmodpath = path
    
    def __init__(self):
        mods = os.listdir('mods')
        
        self.mods = {}

        for file in mods:
            path = f'mods{os.sep}{file}{os.sep}'
            
            if os.path.isdir(path) and not file == '__pycache__':
                self._set_modpath(path)
                
                mod = importlib.import_module(f'mods.{file}')
                
                if not hasattr(mod, 'on_load'):
                    print(f'Error: mod {file} has no attribute on_load')
                else:
                    self.mods[file] = {
                        'module': mod,
                        'path': path}
        
        self.handlers = {
            'init_mapgen': [],
            'on_player_join': [],
            'on_player_leave': [],
        }
        
    def load_mods(self, names=None):
        mods = []
        
        if names is None:
            names = self.mods.keys()  # Load all by default
        
        for name in names:
            if self.mods.get(name):
                self._set_modpath(self.mods[name]['path'])
                
                self.mods[name]['module'].on_load(self)

                mods.append(self.mods[name]['module'])
            else:
                print(f'Error: could not find mod {name}')
        
        self._set_modpath(None)
        
        return mods
    
    def add_handler(self, **kwargs):
        for name in kwargs.keys():
            if self.handlers.get(name) is None:
                print(f'Warning: no such handler: {name}')
                traceback.print_stack()
                continue
            
            self.handlers[name].append(kwargs[name])
    
    def call_handlers(self, name, *args, **kwargs):
        if self.handlers.get(name) is None:
            print(f'Warning: no such handler: {name}')
            traceback.print_stack()
        else:
            for handler in self.handlers[name]:
                handler(*args, **kwargs)


def modpath(path=''):
    return f"{ModManager.curmodpath}{path}"

def getmanager():
    return ModManager.get()
