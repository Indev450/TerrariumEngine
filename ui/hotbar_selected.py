from .label import Label

from game.texture import gettexture


class HotbarSelected(Label):
    background = gettexture('resources/textures/ui/selected.png')
