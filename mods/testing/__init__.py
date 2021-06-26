from .items import DebugPick, DebugAxe, MusicItem, Pistol
from .blocks import Terminal
from .entities import Bullet


def on_load(modmanager):
    DebugPick.register()
    DebugAxe.register()
    MusicItem.register()
    Pistol.register()
    
    Terminal.register()
    
    Bullet.register()
    
    modmanager.add_handler(on_player_join=on_player_join)


def on_player_join(player):
    inv = player.get_inventory()
    
    if not inv.has_item('testing:debug_pick'):
        inv.add_item('main', 'testing:debug_pick')
    
    if not inv.has_item('testing:debug_axe'):
        inv.add_item('main', 'testing:debug_axe')

    if not inv.has_item('testing:music_item'):
        inv.add_item('main', 'testing:music_item')

    if not inv.has_item('testing:terminal'):
        inv.add_item('main', 'testing:terminal')
        
    if not inv.has_item('testing:pistol'):
        inv.add_item('main', 'testing:pistol')
