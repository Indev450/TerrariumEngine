from .item import Item
import game.block as block


def register_block_item(blockdef):
    class BlockItem(Item):
        ID = blockdef.id
        image = blockdef.inventory_image or blockdef.tile
        
        on_press = block._place_block(blockdef.id, blockdef.layer)
        on_keep_press = block._place_block_keep(blockdef.id, blockdef.layer)
    
    BlockItem.register()
    
    return BlockItem
    
