from .entity import Entity

from .texture import gettransparent

from .item_stack import ItemStack


class ItemEntity(Entity):
    ID = 'builtin:item_entity'
    
    @classmethod
    def from_save(cls, manager, uuid, save):
        ientity = super().from_save(manager, uuid, save)
        
        istack = ItemStack().load(save['data']['stack'])
        
        ientity.set_item_stack(istack)
        
        return ientity
    
    def __init__(self,
                 manager=None,
                 uuid=None,
                 position=(0, 0),
                 velocity=(0, 0)):
        super().__init__(manager=manager,
                         uuid=uuid,
                         position=position,
                         velocity=velocity,
                         size=(10, 10))
        
        self.item_stack = None
        
        self.image = gettransparent(10, 10)
        
        self.add_tag('itementity')
        
    def set_item_stack(self, item_stack):
        self.item_stack = item_stack
        
        if item_stack.empty():
            self.manager.delentity(self.uuid)
        else:
            self.image = item_stack.item_t.image
    
    def update(self, dtime):
        if self.item_stack.empty():
            return  # Do not update empty item entities
        
        super().update(dtime)
        
        for player in self.manager.get_tagged_entities('player'):
            if player.rect.colliderect(self.rect):
                self.item_stack.item_t.on_picked_up(player, self.item_stack)
                
                player.get_inventory().add_item_stack('hotbar', self.item_stack)
                
                if not self.item_stack.empty():
                    player.get_inventory().add_item_stack('main', self.item_stack)
                
                self.set_item_stack(self.item_stack)
    
    def on_save(self):
        if self.item_stack.empty():
            return  # Do not save empty item entities
        return {
            'stack': self.item_stack.dump()
        }
