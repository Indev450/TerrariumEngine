import json
import os
import importlib
import argparse

config = None


def _get_config():
    file = open("mgconfig.json", 'r')

    config = json.load(file)

    return config


def get_config():
    try:
        return _get_config()
    except (FileNotFoundError, json.JSONDecodeError):
        print("Config file does not exist or corrupted, creating new")

        config = {
            "mapgens": {
                "mapgenv1": {
                    "name": "Mapgen V1",
                    "description": "Default Terrarium mapgen",
                    "module": "mapgen.mapgenv1",
                }
            }
        }

        write_config(config)

        return config


def write_config(config):
    file = open("mgconfig.json", 'w')

    json.dump(config, file)


def register_mapgen(name, mgconfig):
    global config

    if config is None:
        config = get_config()

    config["mapgens"][name] = mgconfig

    write_config(config)


def run_mapgen(mapgen, mods, output, width, height):
    import game.stdblocks
    global config

    if config is None:
        config = get_config()

    mgconfig = config["mapgens"].get(mapgen)

    if mgconfig is None:
        raise NameError(f"mapgen {mapgen} does not exist or not registered")

    importlib.import_module(mgconfig["module"]).get_mapgen()(
        mods=[importlib.import_module(module) for module in mods],
        output=output,
        width=width,
        height=height).run()


def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--mapgen", default="mapgenv1")
    parser.add_argument("--mods", default="")
    parser.add_argument("--output", default="world.tworld")
    parser.add_argument("--width", default="1000")
    parser.add_argument("--height", default="500")

    args = parser.parse_args()

    mods = []

    for mod in args.mods.split(':'):
        if mod:
            mods.append(mod)

    run_mapgen(args.mapgen,
               mods,
               args.output,
               int(args.width),
               int(args.height))


if __name__ == '__main__':
    main()
