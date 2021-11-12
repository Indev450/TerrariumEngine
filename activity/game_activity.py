import os

import pygame as pg

import game.texture as textures
import game.sound as sounds

from game.block import BlockDefHolder
from game.player import Player
from game.item_entity import ItemEntity
from game.camera import Camera
from game.world import World
from game.meta_manager import MetaManager
from game.entity_manager import EntityManager
from game.item import Item
from game.sound import getsound
from game.decorations import DecorationManager
from game.craft import CraftManager

from mods.manager import ModManager

from ui.label import Label
from ui.button import Button
from ui.inv_hotbar import InventoryHotbar
from ui.hotbar_selected import HotbarSelected
from ui.inventory_cell import InventoryCell
from ui.craftui import CraftUI
from ui.healthbar import HealthBar

from utils.calls import Call, WeakCall

from worldfile.worldfile import decode, encode

from .activity import Activity, newactivity
from .default_parallax import DefaultParallax

import activity.main_menu_activity as mainmenu  # Cannot import MainMenuActivity because of cirlular import

from config import getcfg


config = getcfg()


class GameActivity(Activity):
    BG_COLOR = pg.Color(config["game.background"])
    
    BG_MUSIC = getsound(config["game.music"])  # TODO - play music based on biome
    
    INTERACT_DIST = config["player.interact_distance"]
    
    def __init__(self, path):
        super().__init__()
        
        self.ui_visible = False
        
        savepath = os.path.join('saves', path)
        self.worldpath = os.path.join(savepath, 'world.tworld')
        self.liquids_path = os.path.join(savepath, 'world.liquids')
        self.metapath = os.path.join(savepath, 'world.meta')
        self.entitiespath = os.path.join(savepath, 'world.entities')
        
        self.meta_manager = MetaManager.load(self.metapath)
        
        modmanager = ModManager.get()
        
        modmanager.reset_handlers()
        modmanager.load_mods((self.meta_manager.getmeta('modprofile') or {'name': '_all'})['name'])
        
        textures.reload()  # Reload all textures from mods
        sounds.reload()  # Same with sounds
        
        preserved_block_ids = self.meta_manager.getmeta('preserved_block_ids')
        
        if preserved_block_ids is None:
            _, preserved_block_ids = self.meta_manager.newmeta('preserved_block_ids')
        
        BlockDefHolder.init_int_ids(preserved_block_ids)  # Create int identifiers for
                                                          # block definitions
        
        Player.register()
        ItemEntity.register()

        Camera.init()  # Create camera object
        
        self.parallax = DefaultParallax()
        
        self.decormanager = DecorationManager.new()

        self.background = pg.Surface(
            (self.app.WIN_WIDTH, self.app.WIN_HEIGHT))
        self.background.fill(self.BG_COLOR)
        
        file = open(self.worldpath, 'rb')
        
        decoded = decode(file.read())
        
        file.close()

        self.world = World.new(*decoded)
        
        try:
            file = open(self.liquids_path, 'rb')
            self.world.liquid_manager.deserialize(file.read())
        except FileNotFoundError:
            pass
        
        self.entity_manager = EntityManager.new()
        self.entity_manager.load(self.entitiespath)
        
        modmanager.call_handlers('on_world_load', self.world)
        
        self.player = self.entity_manager.getentity('player')
        
        if not self.player:
            self.player, _ = self.entity_manager.newentity('builtin:player', 'player')
            self.player.respawn()  # Go to spawnpoint
        
        # Currently i have no idea how to fix issue with player entity use-after-free,
        # so i'm keeping it as a strong reference. That should not become problem
        # because even being alive after GameActivity closed, player deleted
        # when starting new GameActivity. But this is still bad, so i'll need
        # to fix that later.
        self.player = self.player.obj()
        
        inv = self.player.get_inventory()
        
        modmanager.call_handlers('on_player_join', self.player)
        
        win_width, win_height = config["app.resolution"]
        
        ################################################################
        # Hotbar
        hotbar = InventoryHotbar(
            position=(20, 20),
            size=(510, 70))
            
        inv_width = inv.get_size('hotbar')
        inv_height = inv.get_size('main') // inv_width
        
        cell_size = 50
        space = 10

        for i in range(inv_width):
            x = (i+1)*space + cell_size*i + space
            InventoryCell(inv.get_item_ref('hotbar', i),
                          inv,
                          parent=hotbar,
                          position=(x, space),
                          size=(cell_size, cell_size))
        
        x = (self.player.selected_item+1)*space + cell_size*self.player.selected_item + space
        self.hotbar_selected = HotbarSelected(
                          parent=hotbar,
                          position=(x, space),
                          size=(cell_size, cell_size))
        
        self.overlay.add_element('hotbar', hotbar, True)
        
        ################################################################
        # Main inventory
        main_inventory = InventoryHotbar(
            position=(20, 140),
            size=(510, 280))

        for x in range(inv_width):
            for y in range(inv_height):
                InventoryCell(inv.get_item_ref('main', y*inv_width + x),
                              inv,
                              parent=main_inventory,
                              position=((x+1)*space + cell_size*x + space, 
                                        (y+1)*space + cell_size*y + space),
                              size=(cell_size, cell_size))

        self.overlay.add_element('inventory', main_inventory)
        
        ################################################################
        # Pause
        pause = Label(
            text="Paused",
            position=(win_width//2 - 250, win_height/2 - 220),
            size=(500, 400))
        
        Button(
            parent=pause,
            on_pressed=WeakCall(self.play),
            text="Continue",
            position=(100, 100),
            size=(300, 100))
        
        Button(
            parent=pause,
            on_pressed=Call(newactivity, mainmenu.MainMenuActivity),
            text="Quit",
            position=(100, 220),
            size=(300, 100))
        
        self.overlay.add_element('pause', pause)
        
        ################################################################
        # Craft UI
        self.craftui = CraftUI(position=(540, 140))
        self.craftui.set_crafts(self.player, 'builtin:emptyhands')
        
        self.overlay.add_element('craftui', self.craftui.root)

        self.camera = Camera.get()
        self.camera.set_obj(self.player)
        self.camera.set_offset(self.app.WIN_WIDTH/2, self.app.WIN_HEIGHT/2)
        
        ################################################################
        # Health Bar
        self.overlay.add_element('healthbar', HealthBar(
            self.player,
            position=(config["app.resolution"][0] - 350 - 10, 10),
            size=(350, 60)),
            True)

        self.controls = {
            'left': False,
            'right': False,
            'up': False,
            'mouse': {
                'lmb': {
                    'pressed': False,
                    'press_time': 0,
                },
                'rmb': {
                    'pressed': False,
                    'press_time': 0,
                }
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
    
    def open_inventory(self, inv, name, length):
        inv_width = length
        inv_height = inv.get_size(name) // length
        
        cell_size = 50
        space = 10
        
        inventory = InventoryHotbar(
            position=(20, 440),
            size=(510, 280))

        for x in range(inv_width):
            for y in range(inv_height):
                InventoryCell(inv.get_item_ref(name, y*inv_width + x),
                              self.player.inventory,
                              parent=inventory,
                              position=((x+1)*space + cell_size*x + space,
                                        (y+1)*space + cell_size*y + space),
                              size=(cell_size, cell_size))
        
        self.overlay.add_element('opened_inventory', inventory, True)
        self.toggle_inventory_visibility()
    
    def update_selected_item(self):
        inv_width = self.player.inventory.get_size('hotbar')
        inv_height = self.player.inventory.get_size('main') // inv_width
        
        cell_size = 50
        space = 10
        
        x = (self.player.selected_item+1)*space + cell_size*self.player.selected_item
        
        self.hotbar_selected.set_rect(
            position=(x+space, space),
            size=(cell_size, cell_size))
    
    def toggle_inventory_visibility(self):
        if self.overlay.is_visible('inventory'):
            if self.overlay.get('opened_inventory') is not None:
                self.overlay.hide('opened_inventory')
            
            if self.overlay.is_visible('craftui'):
                self.overlay.hide('craftui')
            
            self.overlay.hide('inventory')
            
            self.ui_visible = False
        else:
            self.overlay.show('inventory')
            self.ui_visible = True
    
    def show_craft_menu(self, type):
        self.craftui.set_crafts(self.player, type)
        
        self.overlay.show('craftui')
        
        if not self.overlay.is_visible('inventory'):
            self.toggle_inventory_visibility()

    def update(self, dtime):
        if self._skipupdate:
            self._skipupdate = False
            return

        if not self.paused:
            if ((self.controls['mouse']['lmb']['pressed'] or self.controls['mouse']['rmb']['pressed'])
                and self.player.hp > 0):
                istack = self.player.inventory.get_item('hotbar', self.player.selected_item)
                
                if not istack.empty():
                    x, y = pg.mouse.get_pos()
                    
                    cam_x, cam_y = self.camera.get_position()
                    
                    x += cam_x
                    y += cam_y
                    
                    if self.controls['mouse']['lmb']['pressed']:
                        if self.controls['mouse']['lmb']['press_time'] == 0:
                            istack.item_t.on_press(self.player, istack, (x, y))
                            self.controls['mouse']['lmb']['press_time'] += dtime
                        else:
                            istack.item_t.on_keep_press(
                                self.player,
                                istack,
                                (x, y), 
                                self.controls['mouse']['lmb']['press_time'])
                            self.controls['mouse']['lmb']['press_time'] += dtime
                    
                    elif self.controls['mouse']['rmb']['pressed']:
                        if self.controls['mouse']['rmb']['press_time'] == 0:
                            istack.item_t.alt_on_press(self.player, istack, (x, y))
                            self.controls['mouse']['rmb']['press_time'] += dtime
                        else:
                            istack.item_t.alt_on_keep_press(
                                self.player,
                                istack,
                                (x, y), 
                                self.controls['mouse']['rmb']['press_time'])
                            self.controls['mouse']['rmb']['press_time'] += dtime

            self.player.update_presses(left=False if self.ui_visible else self.controls['left'],
                                       right=False if self.ui_visible else self.controls['right'],
                                       up=False if self.ui_visible else self.controls['up'])
            self.entity_manager.update(dtime)

            self.world.update(dtime)
            
            self.decormanager.update(dtime)

            self.camera.update_position()

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        
        self.parallax.draw(screen)

        self.world.draw(screen)
        
        self.entity_manager.draw(screen)
        
        self.decormanager.draw(screen)
        
        self.world.draw_liquids(screen)

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
        if self.paused:
            super().on_event(event)
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                self.controls['left'] = True

            elif event.key == pg.K_d:
                self.controls['right'] = True

            elif event.key == pg.K_SPACE:
                self.controls['up'] = True
            
            elif event.key == pg.K_i:
                self.toggle_inventory_visibility()
            
            elif event.key == pg.K_e:
                self.interact()
            
            elif event.key == pg.K_c:
                if self.overlay.is_visible('craftui'):
                    self.overlay.hide('craftui')
                else:
                    self.show_craft_menu('builtin:emptyhands')
            
            elif event.key == pg.K_ESCAPE:
                if self.overlay.is_visible('inventory'):
                    if self.overlay.is_visible('craftui'):
                        self.overlay.hide('craftui')
                        return
                    
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

        elif event.type == pg.MOUSEBUTTONDOWN and not self.ui_visible:
            if event.button == 1:
                self.controls['mouse']['lmb']['pressed'] = True
            elif event.button == 3:
                self.controls['mouse']['rmb']['pressed'] = True
            elif event.button in (4, 5):
                self.player.selected_item += 1 if event.button == 5 else -1
                
                if self.player.selected_item < 0:
                    self.player.selected_item = self.player.inventory.get_size('hotbar')-1
                elif self.player.selected_item >= self.player.inventory.get_size('hotbar'):
                    self.player.selected_item = 0
                
                self.update_selected_item()
        
        elif event.type == pg.MOUSEBUTTONUP and not self.ui_visible:
            if event.button in (1, 3):
                istack = self.player.inventory.get_item('hotbar', self.player.selected_item)
                
                if not istack.empty():
                    x, y = pg.mouse.get_pos()
                    
                    cam_x, cam_y = self.camera.get_position()
                    
                    x += cam_x
                    y += cam_y
                    
                    if event.button == 1:
                        istack.item_t.on_release(self.player, istack, (x, y))
                    
                    else:
                        istack.item_t.alt_on_release(self.player, istack, (x, y))
                
                if event.button == 1:
                    self.controls['mouse']['lmb']['pressed'] = False
                    self.controls['mouse']['lmb']['press_time'] = 0
                
                else:
                    self.controls['mouse']['rmb']['pressed'] = False
                    self.controls['mouse']['rmb']['press_time'] = 0

        elif not (event.type == pg.MOUSEBUTTONUP and
                  not self.ui_visible):
            super().on_event(event)
    
    def interact(self):
        can_interact = []
        
        # Find all entities we can interact
        for entity in self.entity_manager.get_tagged_entities('interactive'):
            v = pg.math.Vector2(self.player.rect.center)
            
            if v.distance_to(entity.rect.center) <= self.INTERACT_DIST:
                can_interact.append(entity)
        
        if not can_interact:
            return  # No entities found
        
        # Cursor position in the world
        cursor = pg.math.Vector2(pg.mouse.get_pos()) + self.camera.get_position()
        
        # Nearest entity and distance to it. Initialize it with the first found entity
        nearest = (can_interact[0], cursor.distance_to(can_interact[0].rect.center))
        
        # Now find the nearest entity for the cursor
        for entity in can_interact[1:]:
            dist = cursor.distance_to(entity.rect.center)
            
            if dist < nearest[1]:
                nearest = (entity, dist)
        
        nearest[0].on_interact(self.player)
    
    def on_begin(self):
        self.app.music_player.play(self.BG_MUSIC)

    def on_end(self):
        print("Saving world...")
        
        try:
            self.app.music_player.stop()
        except pg.error:
            pass  # When closing game, pygame.mixer becomes not initialized

        blocksize = BlockDefHolder.registered_count()//255 + 1
        
        data = encode(self.world.world_data,
                      self.world.WORLD_WIDTH, self.world.WORLD_HEIGHT)
        
        self.meta_manager.save(self.metapath)
        self.entity_manager.save(self.entitiespath)
        
        with open(self.liquids_path, 'wb') as file:
            file.write(self.world.liquid_manager.serialize())
        
        MetaManager.instance = None
        EntityManager.instance = None
        World.instance = None

        file = open(self.worldpath, 'wb')

        file.write(data)

        file.close()
