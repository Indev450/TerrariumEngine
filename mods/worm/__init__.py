from .entities import WormHead, WormBody, WormSpawner
from .particles import WormParticleMetal, WormParticleSmoke


def on_load(modmanager):
    WormHead.register()
    WormBody.register()
    
    WormParticleMetal.register()
    WormParticleSmoke.register()
    
    modmanager.add_handler(on_world_load=add_spawner)


def add_spawner(world):
    WormSpawner().add_spawn_tick(10)
