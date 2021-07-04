from .item import Item
import game.block as block


def register_block_item(blockdef):
    class BlockItem(Item):
        ID = blockdef.id
        image = blockdef.inventory_image or blockdef.tile
        
        on_keep_press = block._place_block_keep(blockdef.id, blockdef.layer)
    
    if getattr(blockdef, 'wall_id', None) is not None:
        BlockItem.alt_on_keep_press = block._place_block_keep(blockdef.wall_id, 2)
    
    BlockItem.register()
    
    return BlockItem
    
