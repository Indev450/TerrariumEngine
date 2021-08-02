import os
import importlib
import traceback
import json

from game.entity import Entity
from game.block import BlockDefHolder
from game.item import Item

from utils.checks import hasitems

from .jsonblock import register_block

from config import getcfg


config = getcfg()


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
        
        self.modprofiles = config.get("mods.profiles", {})
        
        self.mods = {}

        for name in mods:
            path = os.path.join('mods', name)
            confpath = os.path.join(path, 'modconf.json')
            
            if os.path.isdir(path) and os.path.isfile(confpath):
                with open(confpath) as file:
                    modconf = json.load(file)
                    
                    reqs_found, missing_reqs = hasitems(mods, modconf.get('reqs', []), True)
                    
                    if not reqs_found:
                        print(f'Error: missing requirements for mod {name}: {", ".join(missing_reqs)}')
                        continue
                
                self._set_modpath(path)
                
                mod = importlib.import_module(f'mods.{name}')
                
                self.mods[name] = {
                    'module': mod,
                    'path': path,
                    'modconf': modconf}
        
        self.modprofiles['_all'] = list(self.mods.keys())
        
        self.handlers = {}
    
    def reset_handlers(self):
        self.handlers = {
            'init_mapgen': [],
            'on_player_join': [],
            'on_player_leave': [],
            'on_world_load': [],
        }
        
    def load_mods(self, profile='_all'):
        """Call on_load() for each mod in modprofiles[profile]
        
        If not given, all mods will be initialized (profile '_all')"""
        
        Entity.clear()
        BlockDefHolder.clear()
        Item.clear()
        # Unregister everything
        
        mods = []
        
        names = self.modprofiles[profile]
        
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
        
        return os.path.join('mods', mod, path)
    else:
        return os.path.join(ModManager.curmodpath, path[0])
