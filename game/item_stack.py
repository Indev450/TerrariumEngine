import enum

from .item import Item


class ItemStackChange(enum.Enum):
    '''ItemStack change type'''
    SET_COUNT = enum.auto()
    ADD_ITEMS = enum.auto()
    SET_TYPE = enum.auto()
    SET_DATA = enum.auto()
    CONSUME_ITEMS = enum.auto()


class ItemStack:
    '''Contains info about stored items in this stack'''

    def __init__(self, item_t=None, count=0, data=None):
        self.item_t = item_t

        self.count = 0

        if item_t is not None:
            self.count = item_t.bound_items_count(count)

        if data is not None:
            self.item_data = data
        else:
            self.item_data = {}

        self.on_change = None
    
    def set_change_callback(self, cb):
        '''Sets function which will be called every time when
        item stack changes. function should be this type:
        on_change(itemstack, change)
        itemstack - changed stack
        change = ItemStackChange object
        '''
        self.on_change = cb

    def get_count(self):
        return self.count
    
    def get_data(self, key):
        return self.item_data.get(key)

    def set_count(self, count):
        self.count = count
        
        if count < 1:
            self.item_t = None
            self.item_data = {}

        if self.on_change is not None:
            self.on_change(self, ItemStackChange.SET_COUNT)
    
    def add_items(self, count):
        if self.item_t is None:
            return
        
        left = self.count + count - self.item_t.maxcount
        
        self.count = self.item_t.bound_items_count(self.count + count)
        
        if self.on_change is not None:
            self.on_change(self, ItemStackChange.ADD_ITEMS)
        
        return left if left > 0 else 0
    
    def consume_items(self, count):
        self.add_items(-count)
        
        if self.on_change is not None:
            self.on_change(self, ItemStackChange.CONSUME_ITEMS)

    def set_type(self, item_t, count=0, data=None):
        self.item_t = item_t

        if item_t is not None:
            self.count = item_t.bound_items_count(count)

        if data is not None:
            self.item_data = data
        else:
            self.item_data = {}

        if self.on_change is not None:
            self.on_change(self, ItemStackChange.SET_TYPE)
    
    def set_data(self, key, value):
        self.item_data[key] = value
        
        if self.on_change is not None:
            self.on_change(self, ItemStackChange.SET_DATA)
    
    def can_merge(self, itemstack):
        if self.item_t is not None:
            return self.item_t.can_merge(self, itemstack)
        return True
    
    def merge(self, itemstack):
        if self.item_t is None:
            self.set_type(itemstack.item_t,
                          itemstack.get_count(),
                          itemstack.item_data)
            
            itemstack.set_type(None)
        elif self.can_merge(itemstack):
            left = self.add_items(itemstack.get_count())
            
            if left != 0:
                itemstack.set_count(left)
            else:
                itemstack.set_type(None)

    def empty(self):
        return self.count <= 0 or self.item_t is None
    
    def dump(self):
        ID = ''
        
        if self.item_t is not None:
            ID = self.item_t.ID
        
        return {
            'ID': ID,
            'count': self.count,
            'data': self.item_data,
        }
    
    def load(self, save):
        item_t = Item.get(save['ID'])
        count = save['count']
        data = save['data']
        
        self.set_type(item_t, count, data)
        
        return self
