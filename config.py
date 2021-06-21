"""Module for loading and storing configuration file"""
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
