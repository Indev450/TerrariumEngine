import traceback

from .item_stack import ItemStack

from .item import Item


class Inventory:

    def __init__(self, owner=None):
        self.data = {}
        self.owner = owner

    def set_size(self, name, size):
        if self.data.get(name) is None:
            self.data[name] = []

        new = []

        for i in range(size):
            if i < len(self.data[name]):
                new.append(self.data[name][i])
            else:
                new.append(ItemStack())

        self.data[name] = new

    def get_size(self, name):
        return len(self.data.get(name, []))
    
    def get_item(self, name, index):
        try:
            return self.data.get(name, [])[index]
        except IndexError:
            import traceback

            traceback.print_stack()

            print('Error: wrong inventory name or index')
    
    def set_item(self, name, index, item_t=None, count=0, data={}):
        try:
            self.data.get(name, [])[index].set_type(item_t, count, data)
        except IndexError:
            import traceback

            traceback.print_stack()

            print('Error: wrong inventory name or index')

    def get_item_ref(self, name, index):
        return InventoryRef(self, name, index)
    
    def swap(self, name1, index1, name2, index2):
        itemstack1 = self.get_item(name1, index1)
        item_t1, count1, data1 = itemstack1.item_t, itemstack1.count, itemstack1.item_data

        itemstack2 = self.get_item(name2, index2)
        item_t2, count2, data2 = itemstack2.item_t, itemstack2.count, itemstack2.item_data
        
        if itemstack1.can_merge(itemstack2):
            leftover = itemstack1.merge(itemstack2)
        else:
            itemstack1.set_type(item_t2, count2, data2)
            itemstack2.set_type(item_t1, count1, data1)
    
    def add_item(self, name, item, count=1, data=None):
        if self.data.get(name) is None:
            print(f'Error: could not find inventory {name}')
            traceback.print_stack()
            return
        
        item_t = Item.get(item)
        
        if item_t is None:
            print(f'Warning: no such item: {item}')
            traceback.print_stack()
            return
        
        istack = ItemStack(item_t, count, data)
        
        return self.add_item_stack(name, istack)

    def add_item_stack(self, name, istack):
        for i in range(len(self.data[name])):
            origstack = self.data[name][i]
            
            origstack.merge(istack)

            if istack.empty():
                return istack
                
        return istack
    
    def has_item(self, item, count=1):
        item_t = Item.get(item)
        
        if item_t is None:
            print(f'Warning: no such item: {item}')
            return False
        
        for name in self.data.keys():
            for istack in self.data[name]:
                if istack.item_t is item_t:
                    count -= istack.get_count()
                    
                    if count <= 0:
                        return True
        
        return False
    
    def dump(self):
        result = {}
        
        for key in self.data:
            result[key] = []
            
            for item in self.data[key]:
                result[key].append(item.dump())
        
        return result
    
    def load(self, data):
        self.data = {}
        
        for key in data:
            self.data[key] = []
            
            for item in data[key]:
                self.data[key].append(ItemStack().load(item))
        
        return self


class InventoryRef:

    def __init__(self, inventory, name, index):
        self.inventory = inventory

        self.name = name

        self.index = index

    def __call__(self):
        return self.inventory.get_item(self.name, self.index)
