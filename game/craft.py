from ui.button import Button

from game.item import Item


class Craft:
    ID = 'builtin:craft'
    TYPE = 'builtin:emptyhands'
    
    inputs = []
    output = None
    
    @classmethod
    def missing_inputs(cls, player):
        missing = []
        
        for item, count in cls.get_inputs():
            if not player.inventory.has_item(item.ID, count):
                missing.append((item, count))
        
        return missing
    
    @classmethod
    def can_craft(cls, player):
        return not cls.missing_inputs(player)
    
    @classmethod
    def do_craft(cls, player):
        if cls.can_craft(player):
            for item, count in cls.get_inputs():
                player.inventory.consume_items(item.ID, count)
            
            output = cls.get_output()
            player.inventory.add_item('main', output[0].ID, output[1])
    
    @classmethod
    def register(cls):
        CraftManager.get().register_craft(cls)
    
    @classmethod
    def get_inputs(cls):
        return parse_items(cls.inputs)
    
    @classmethod
    def get_output(cls):
        return parse_item(cls.output)


class CraftManager:
    instance = None
    
    @classmethod
    def get(cls):
        if cls.instance is None:
            cls.instance = cls()
        return cls.instance
    
    def __init__(self):
        self.crafts = {
            'builtin:emptyhands': {},
        }
    
    def register_craft(self, craft):
        self.crafts[craft.TYPE] = self.crafts.get(craft.TYPE, {})
        
        self.crafts[craft.TYPE][craft.ID] = craft


def parse_items(items):
    result = []
    
    for item in items:
        result.append(parse_item(item))
    
    return result


def parse_item(item):
    """
    Convert item to tuple (item_t, count)

    parse_item(str) -> (Item, int)
    parse_item((Item, int)) -> (Item, int)
    parse_item(Item) -> (Item, 1)
    """
    
    if isinstance(item, str):
        id, *count = item.split()
        
        if not count:
            count = 1
        else:
            count = int(count[0])
        
        return (Item.get(id), count)

    elif isinstance(item, tuple):
        return item

    elif isinstance(item, Item):
        return (item, 1)
