import os

import pygame as pg

import game.texture as textures
import game.sound as sounds

from game.block import Block
from game.player import Player
from game.item_entity import ItemEntity
from game.camera import Camera
from game.world import World, blocks2ids
from game.meta_manager import MetaManager
from game.entity_manager import EntityManager
from game.item import Item
from game.sound import getsound

from mods.manager import getmanager

from ui.label import Label
from ui.inv_hotbar import InventoryHotbar
from ui.hotbar_selected import HotbarSelected
from ui.inventory_cell import InventoryCell

from worldfile.worldfile import decode, encode

from .activity import Activity

from config import getcfg


config = getcfg()


class GameActivity(Activity):
    BG_COLOR = pg.Color(config["game.background"])
    
    BG_MUSIC = getsound(config["game.music"])  # TODO - play music based on biome

    def __init__(self, path):
        super().__init__()
        
        modmanager = getmanager()
        
        modmanager.load_mods()
        
        textures.reload()  # Reload all textures from mods
        sounds.reload()  # Same with sounds

        Block.sort_registered_entries()  # Create int identifiers for
                                         # block definitions
        Player.register()
        ItemEntity.register()

        Camera.init()  # Create camera object

        self.background = pg.Surface(
            (self.app.WIN_WIDTH, self.app.WIN_HEIGHT))
        self.background.fill(self.BG_COLOR)
        
        savepath = os.path.join('saves', path)
        self.worldpath = os.path.join(savepath, 'world.tworld')
        self.metapath = os.path.join(savepath, 'world.meta')
        self.entitiespath = os.path.join(savepath, 'world.entities')
        
        file = open(self.worldpath, 'rb')
        
        blocks = decode(file.read())
        
        file.close()

        self.world = World(*blocks)
        
        self.meta_manager = MetaManager.load(self.metapath)
        
        self.entity_manager = EntityManager.new()
        self.entity_manager.load(self.entitiespath)

        self.player = self.entity_manager.getentity('player')

        if self.player is None:
            self.player, _ = self.entity_manager.newentity('builtin:player', 'player')
        
        inv = self.player.get_inventory()
        
        modmanager.call_handlers('on_player_join', self.player)

        hotbar = InventoryHotbar(
            position_f=(0.1, 0.01),
            size_f=(0.8, 0.14))
            
        inv_width = inv.get_size('hotbar')
        inv_height = inv.get_size('main') // inv_width
        
        cell_width = 0.1
        cell_height = 0.2
        
        space_x = (0.9 - cell_width*inv_width) / (inv_width + 1)  # Rockets go brrr
        space_y = (0.9 - cell_height*inv_height) / inv_height
        # Free space between slots
        
        offset = 0.05

        for i in range(inv_width):
            x = (i+1)*space_x + 0.1*i
            InventoryCell(inv.get_item_ref('hotbar', i),
                          parent=hotbar,
                          position_f=(x+offset, 0.1),
                          size_f=(cell_width, 0.8))
        
        x = (self.player.selected_item+1)*space_x + 0.1*self.player.selected_item
        self.hotbar_selected = HotbarSelected(
                          parent=hotbar,
                          position_f=(x+offset, 0.1),
                          size_f=(cell_width, 0.8))

        main_inventory = InventoryHotbar(
            position_f=(0.1, 0.2),
            size_f=(0.8, 0.6))

        for x in range(inv_width):
            for y in range(inv_height):
                InventoryCell(inv.get_item_ref('main', y*inv_width + x),
                              parent=main_inventory,
                              position_f=((x+1)*space_x + cell_width*x + offset, 
                                          space_y*y + cell_height*y + offset),
                              size_f=(cell_width, cell_height))
        
        self.overlay.add_element('hotbar', hotbar, True)
        self.overlay.add_element('inventory', main_inventory)

        self.camera = Camera.get()
        self.camera.set_obj(self.player)
        self.camera.set_offset(self.app.WIN_WIDTH/2, self.app.WIN_HEIGHT/2)

        self.controls = {
            'left': False,
            'right': False,
            'up': False,
            'mouse': {
                'pressed': False,
                'press_time': 0,
                },
        }

        self.paused = False
        
        self.allow_event(pg.KEYUP)
        self.allow_event(pg.KEYDOWN)
        
        self._skipupdate = True
        # Loading blocks is too long process, so after is dtime becomes
        # a little bigger than often, so entities can teleport pass
        # blocks. This is temporary solution.
        # TODO - fix that problem by better way
    
    def update_selected_item(self):
        inv_width = self.player.inventory.get_size('hotbar')
        inv_height = self.player.inventory.get_size('main') // inv_width
        
        cell_width = 0.1
        cell_height = 0.2
        
        space_x = (0.9 - cell_width*inv_width) / (inv_width + 1)  # Rockets go brrr
        space_y = (0.9 - cell_height*inv_height) / inv_height
        # Free space between slots
        
        offset = 0.05
        
        x = (self.player.selected_item+1)*space_x + 0.1*self.player.selected_item
        
        self.hotbar_selected.set_rect(
            position_f=(x+offset, 0.1),
            size_f=(cell_width, 0.8))
    
    def toggle_inventory_visibility(self):
        if self.overlay.is_visible('inventory'):
            self.overlay.hide('inventory')
        else:
            self.overlay.show('inventory')

    def update(self, dtime):
        if self._skipupdate:
            self._skipupdate = False
            return
            
        if not self.paused:
            if self.controls['mouse']['pressed']:
                istack = self.player.inventory.get_item('hotbar', self.player.selected_item)
                
                if not istack.empty():
                    x, y = pg.mouse.get_pos()
                    
                    cam_x, cam_y = self.camera.get_position()
                    
                    x += cam_x
                    y += cam_y
                    
                    x = int(x//Block.WIDTH)
                    y = int(y//Block.HEIGHT)
                    
                    if self.controls['mouse']['press_time'] == 0:
                        istack.item_t.on_press(self.player, istack, (x, y))
                        self.controls['mouse']['press_time'] += dtime
                    else:
                        istack.item_t.on_keep_press(
                            self.player,
                            istack,
                            (x, y), 
                            self.controls['mouse']['press_time'])
                        self.controls['mouse']['press_time'] += dtime

            self.player.update_presses(left=self.controls['left'],
                                       right=self.controls['right'],
                                       up=self.controls['up'])
            self.entity_manager.update(dtime)

            self.world.update(dtime)

            self.camera.update_position()

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        self.world.draw(screen)
        
        self.entity_manager.draw(screen)

    def pause(self):
        self.overlay.show('pause')
        self.paused = True

    def play(self):
        self.overlay.hide('pause')
        self.paused = False
    
    def toggle_pause(self):
        if self.paused:
            self.play()
        else:
            self.pause()

    def on_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                self.controls['left'] = True

            elif event.key == pg.K_d:
                self.controls['right'] = True

            elif event.key == pg.K_SPACE:
                self.controls['up'] = True
            
            elif event.key == pg.K_i:
                self.toggle_inventory_visibility()
            
            elif event.key == pg.K_ESCAPE:
                if self.overlay.is_visible('inventory'):
                    self.toggle_inventory_visibility()
                else:
                    self.toggle_pause()

        elif event.type == pg.KEYUP:
            if event.key == pg.K_a:
                self.controls['left'] = False

            elif event.key == pg.K_d:
                self.controls['right'] = False

            elif event.key == pg.K_SPACE:
                self.controls['up'] = False

        elif event.type == pg.MOUSEBUTTONDOWN and not self.overlay.is_visible('inventory'):
            if event.button == 1:
                self.controls['mouse']['pressed'] = True
            elif event.button in (4, 5):
                self.player.selected_item += 1 if event.button == 5 else -1
                
                if self.player.selected_item < 0:
                    self.player.selected_item = self.player.inventory.get_size('hotbar')-1
                elif self.player.selected_item >= self.player.inventory.get_size('hotbar'):
                    self.player.selected_item = 0
                
                self.update_selected_item()
        
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.controls['mouse']['pressed'] = False
                self.controls['mouse']['press_time'] = 0

        elif not (event.type == pg.MOUSEBUTTONUP and
                  not self.overlay.is_visible()):
            super().on_event(event)
    
    def on_begin(self):
        self.app.music_player.play(self.BG_MUSIC)

    def on_end(self):
        print("Saving world...")
        
        try:
            self.app.music_player.stop()
        except pg.error:
            pass  # When closing game, pygame.mixer becomes not initialized

        blocksize = int(Block.registered_count()/256) + 1

        data = encode(
            blocks2ids(self.world.foreground),
            blocks2ids(self.world.midground),
            blocks2ids(self.world.background),
            blocksize)
        
        self.meta_manager.save(self.metapath)
        self.entity_manager.save(self.entitiespath)

        file = open(self.worldpath, 'wb')

        file.write(data)

        file.close()
