from .label import Label

from game.texture import gettexture


class InventoryHotbar(Label):
    background = gettexture('resources/textures/ui/inventory_hotbar.png')
