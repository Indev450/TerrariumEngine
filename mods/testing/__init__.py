from .items import DebugPick, DebugAxe, DebugSword, MusicItem, Pistol, WaterBucket
from .blocks import Terminal
from .entities import Bullet, SwordSwing


def on_load(modmanager):
    DebugPick.register()
    DebugAxe.register()
    DebugSword.register()
    MusicItem.register()
    Pistol.register()
    WaterBucket.register()
    
    Terminal.register()
    
    Bullet.register()
    SwordSwing.register()
    
    modmanager.add_handler(on_player_join=on_player_join)


def on_player_join(player):
    inv = player.get_inventory()
    
    if not inv.has_item('testing:debug_pick'):
        inv.add_item('main', 'testing:debug_pick')
    
    if not inv.has_item('testing:debug_axe'):
        inv.add_item('main', 'testing:debug_axe')
    
    if not inv.has_item('testing:debug_sword'):
        inv.add_item('main', 'testing:debug_sword')

    if not inv.has_item('testing:music_item'):
        inv.add_item('main', 'testing:music_item')

    if not inv.has_item('testing:terminal'):
        inv.add_item('main', 'testing:terminal')
        
    if not inv.has_item('testing:pistol'):
        inv.add_item('main', 'testing:pistol')
        
    if not inv.has_item('testing:water_bucket'):
        inv.add_item('main', 'testing:water_bucket')
