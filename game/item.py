from game.sound import getsound

import traceback

from config import getcfg


config = getcfg()


class Item:
    image = None
    
    ID = ''
    
    maxcount = config["item.default.maxcount"]
    
    pick_up_sound = getsound(config["item.default.pick_up_sound"])
    
    registered = {}
    
    @classmethod
    def clear(cls):
        cls.registered = {}

    @classmethod
    def on_press(cls, player, itemstack, position):
        '''Called when player starts using item'''
        pass
    
    @classmethod
    def on_keep_press(cls, player, itemstack, position, use_time):
        '''Called when player keeps using item'''
        pass

    @classmethod
    def on_release(cls, player, itemstack, position):
        '''Caled when player stops using item'''
        pass

    @classmethod
    def register(cls):
        if cls.registered.get(cls.ID) is not None:
            traceback.print_stack()
            print(f'Warning: item {cls.ID} already registered')
        cls.registered[cls.ID] = cls
    
    @classmethod
    def on_picked_up(cls, player, itemstack):
        '''Called when player picks item up
        can be used for achievements'''
        pass
    
    @classmethod
    def on_wield_start(cls, player, itemstack):
        '''Called when item selected'''
        pass
    
    @classmethod
    def on_wield_stop(cls, player, itemstack):
        '''Called when item unselected item'''
        pass
    
    @classmethod
    def can_merge(cls, itemstack1, itemstack2):
        '''Returns true if both itemstacks have same item type
        and they don't have any data'''
        return (itemstack1.item_t is itemstack2.item_t and
                not itemstack1.item_data and
                not itemstack2.item_data and
                not (itemstack1.item_t.maxcount == itemstack1.get_count() or
                     itemstack2.item_t.maxcount == itemstack2.get_count()))

    @classmethod
    def bound_items_count(cls, count):
        '''Returns validated item count for an item stack'''
        return max(0, min(cls.maxcount, count))
    
    @classmethod
    def get(cls, id):
        return cls.registered.get(id)
