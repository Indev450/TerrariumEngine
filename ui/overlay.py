class Overlay:
    instance = None

    def __init__(self):
        self.elements = {}
        self.enabled = True

    def add_element(self, name, element, visible=False):
        self.elements[name] = {
            'element': element,
            'visible': visible,
        }

    def get(self, name):
        entry = self.elements.get(name)
        if entry is not None:
            return entry['element']

    def on_press(self, position):
        for name in self.elements.keys():
            if (self.elements[name]['visible'] and 
               self.elements[name]['element'].rect.collidepoint(*position)):
                self.elements[name]['element'].on_click(position)

    def on_release(self, position):
        for name in self.elements.keys():
            if self.elements[name]['visible']: 
               self.elements[name]['element'].on_release(position)

    def on_scroll(self, up):
        for name in self.elements.keys():
            if self.elements[name]['visible']:
                self.elements[name]['element'].on_scroll(up)

    def show(self, name):
        if not self.elements.get(name):
            print(f"Warning: cannot show UI element '{name}', element not found")
            return
        self.elements[name]['visible'] = True

    def hide(self, name):
        if not self.elements.get(name):
            print(f"Warning: cannot hide UI element '{name}', element not found")
            return
        self.elements[name]['visible'] = False

    def draw(self, screen):
        if self.enabled:
            for name in self.elements.keys():
                if self.elements[name]['visible']:
                    self.elements[name]['element'].draw(screen)

    def enable(self):
        self.enabled = True

    def disbale(self):
        self.enabled = False

    def is_enabled(self):
        return self.enabled

    def is_visible(self, name=None):
        if name is not None:
            return self.elements.get(name, {}).get('visible')
        return any([element['visible'] for element in self.elements.values()])


def getoverlay():
    return Overlay.instance

def newoverlay():
    Overlay.instance = Overlay()
    return Overlay.instance

def setoverlay(over):
    Overlay.instance = over
