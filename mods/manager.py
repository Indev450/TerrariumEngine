import os
import importlib
import traceback

from game.entity import Entity
from game.block import BlockDefHolder
from game.item import Item

from .jsonblock import register_block


class ModManager:
    instance = None
    
    curmodpath = ''
    
    @classmethod
    def get(cls):
        """Get mod manager, create if None"""
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
            path = f'mods/{file}/'
            
            if os.path.isdir(path) and not file == '__pycache__':
                self._set_modpath(path)
                
                mod = importlib.import_module(f'mods.{file}')
                
                self.mods[file] = {
                    'module': mod,
                    'path': path}
        
        self.handlers = {}
    
    def reset_handlers(self):
        self.handlers = {
            'init_mapgen': [],
            'on_player_join': [],
            'on_player_leave': [],
            'on_world_load': [],
        }
        
    def load_mods(self, names=None):
        """Call on_load() for each mod in `names`
        
        If not given, all mods will be initialized"""
        
        Entity.clear()
        BlockDefHolder.clear()
        Item.clear()
        # Unregister everything
        
        mods = []
        
        if names is None:
            names = self.mods.keys()  # Load all by default
        
        for name in names:
            if self.mods.get(name):
                mod = self.mods[name]
                
                self._set_modpath(mod['path'])
                
                if hasattr(mod['module'], 'on_load'):
                    mod['module'].on_load(self)
                
                blockspath = f'{mod["path"]}/blocks/'
                
                if os.path.isdir(blockspath):
                    for block in os.listdir(blockspath):
                        register_block(f'{blockspath}/{block}')

                mods.append(self.mods[name]['module'])
            else:
                print(f'Error: could not find mod {name}')
        
        self._set_modpath(None)
        
        return mods
    
    def add_handler(self, **kwargs):
        """Add callback"""
        for name in kwargs.keys():
            if self.handlers.get(name) is None:
                print(f'Warning: no such handler: {name}')
                traceback.print_stack()
                continue
            
            self.handlers[name].append(kwargs[name])
    
    def call_handlers(self, name, *args, **kwargs):
        """Call all added callbacks"""
        if self.handlers.get(name) is None:
            print(f'Warning: no such handler: {name}')
            traceback.print_stack()
        else:
            for handler in self.handlers[name]:
                handler(*args, **kwargs)


def modpath(path=''):
    """Returns path.
    modname:some/path will be turned into mods/modname/some/path
    Regular path will be turned into mods/<current>/<path>"""
    path = path.split(':')
    
    if len(path) == 2:
        mod, path = path
        
        return f'mods/{mod}/{path}'
    else:
        return f'{ModManager.curmodpath}{path[0]}'
