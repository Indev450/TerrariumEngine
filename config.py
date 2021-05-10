"""Module for loading and storing configuration file

Default config:
{
    "app.resolution": [800, 640],
    "app.font": "resources/fonts/dpcomic.ttf",
    "app.font.size": 30,
    "app.maxfps": 60,
    "app.caption": "Terrarium",
    
    "menu.music": "resources/music/mainmenu.ogg",
    "menu.background": "#5555FF",
    
    "game.music": "resources/music/game.ogg",
    "game.background": "#5555FF",
    
    "mapgen.selected": "mapgenv1",
    "mapgen.world_size": [1000, 500],
    
    "chunk.keep_alive_time": 5,
    
    "entity.default.gravity": 25,
    "entity.default.braking": 0.7,
    "entity.default.min_speed": 0.2,
    "entity.default.max_fall": -20,
    
    "item.default.maxcount": 999,
    "item.default.pick_up_sound": "resources/sounds/items/item_pick_up.wav",
    
    "item.entity.try_merge_freq": 1.0,
    "item.entity.merge_dist": 1.5,
    "item.entity.magnet_dist": 2,
    "item.entity.magnet_acceleration": 50,
    
    "player.speed": 30,
    "player.jump": 10,
    "player.size": [20, 40],
    
    "tick.time": 1.0,
    
    "world.chunk_size": [10, 10]
}
"""
import json


file = open('config.json.default')

DEFAULT_CONFIG = json.load(file)

file.close()

config = None


def load():
    global config
    
    try:
        file = open('config.json')
        
        config = json.load(file)
        
        file.close()
    except (FileNotFoundError, json.JSONDecodeError):
        file = open('config.json', 'w')
        
        json.dump(DEFAULT_CONFIG, file, indent=4)
        
        config = DEFAULT_CONFIG
        
        file.close()
    
    updated = False
    
    for key in DEFAULT_CONFIG.keys():
        if key not in config:
            config[key] = DEFAULT_CONFIG[key]
            updated = True
    
    if updated:
        write_config()
    
    return config


def getcfg():
    return config or load()


def write_config():
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)
