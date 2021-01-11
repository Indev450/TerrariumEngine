from .items import DebugPick


def on_load(modmanager):
    DebugPick.register()
    
    modmanager.add_handler(on_player_join=on_player_join)


def on_player_join(player):
    inv = player.get_inventory()
    
    if not inv.has_item('testing:debug_pick'):
        inv.add_item('main', 'testing:debug_pick')
