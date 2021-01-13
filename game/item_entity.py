from pygame.math import Vector2

import game.block as block

from .entity import Entity

from .texture import gettransparent

from .item_stack import ItemStack


class ItemEntity(Entity):
    ID = 'builtin:item_entity'
    
    TRY_MERGE_FREQ = 1.0  # How often item will try to merge with neighbours
    MERGE_DIST = 1.5 * block.Block.WIDTH  # Minimal distance to neighbour to merge
    MAGNET_DIST = 2 * block.Block.WIDTH  # Minimal distance to player to be magneted
    MAGNET_ACCELERATION = 50  # Acceleration of magneted item
    
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
        
        self.item_tag = None
        
        self.merge_timer = 0
        
    def set_item_stack(self, item_stack):
        self.item_stack = item_stack
        
        if item_stack is None or item_stack.empty():
            self.manager.delentity(self.uuid)
        else:
            self.image = item_stack.item_t.image
            
            if self.item_tag is not None:
                self.del_tag(self.item_tag)
            
            self.item_tag = f'itementity:{item_stack.item_t.ID}'
            self.add_tag(self.item_tag)
    
    def merge(self, ientity, dtime, v=None):
        if v is None:
            v = Vector2(1)
        
        self.item_stack.merge(ientity.item_stack)
        
        self.set_item_stack(self.item_stack)
        
        ientity.set_item_stack(ientity.item_stack)
        
        self.yv -= self.MAGNET_ACCELERATION * dtime * v.y + 2
        self.xv -= self.MAGNET_ACCELERATION * dtime * v.x
        # Visualize item merge (+ 2 here just for better effect)
    
    def try_merge(self, dtime):
        for ientity in self.manager.get_tagged_entities(self.item_tag):            
            if ientity is self:
                continue  # Cannot merge with self

            v = Vector2(self.rect.centerx - ientity.rect.centerx,
                        self.rect.centery - ientity.rect.centery)
            
            if v.length() <= self.MERGE_DIST:
                try:
                    v.normalize_ip()
                except ValueError:
                    pass  # Can't normalize Vector of length Zero 
                
                self.merge(ientity, dtime, v)
    
    def update(self, dtime):
        if self.item_stack.empty():
            return  # Do not update empty item entities
        
        super().update(dtime)
        
        for player in self.manager.get_tagged_entities('player'):
            v = Vector2(self.rect.centerx - player.rect.centerx,
                        self.rect.centery - player.rect.centery)
            
            if v.length() <= self.MAGNET_DIST:
                self.ignore_collision = True
                
                v.normalize_ip()
                
                self.xv -= self.MAGNET_ACCELERATION * dtime * v.x
                self.yv -= self.MAGNET_ACCELERATION * dtime * v.y
            else:
                self.ignore_collision = False
            
            if player.rect.colliderect(self.rect):
                self.item_stack.item_t.on_picked_up(player, self.item_stack)
                
                if self.item_stack.item_t.pick_up_sound is not None:
                    self.item_stack.item_t.pick_up_sound.play()
                
                player.get_inventory().add_item_stack('hotbar', self.item_stack)
                
                if not self.item_stack.empty():
                    player.get_inventory().add_item_stack('main', self.item_stack)
                
                self.set_item_stack(self.item_stack)
        
        self.merge_timer += dtime
        
        if self.merge_timer >= self.TRY_MERGE_FREQ:
            self.try_merge(dtime)
            
            self.merge_timer = 0
    
    def on_save(self):
        if self.item_stack.empty():
            return  # Do not save empty item entities
        return {
            'stack': self.item_stack.dump()
        }
