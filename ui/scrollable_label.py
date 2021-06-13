from .label import Label


class ScrollableLabel(Label):
    
    def __init__(self,
                 scroll_step=10,
                 max_scroll=0,
                 text="",
                 parent=None,
                 children=None,
                 position=(0, 0),
                 size=(100, 100)):
        super().__init__(text=text,
                       parent=parent,
                       children=children,
                       position=position,
                       size=size)
        self.max_scroll = max_scroll
        self.scroll = 0
        self.scroll_step = scroll_step
        
    
    def on_scroll(self, position, up):
        scroll = True
        
        for child in self.children:
            if child.rect.collidepoint(*position):
                child.on_scroll(position, up)
            
            if isinstance(child, ScrollableLabel):
                scroll = False
        
        if not scroll:
            return
        
        if 0 <= (self.scroll + self.scroll_step * (-1 if up else 1)) <= self.max_scroll:
            self.scroll += self.scroll_step * (-1 if up else 1)
            for child in self.children:
                child.position = (child.position[0],
                                  child.position[1] + self.scroll_step * (1 if up else -1))
                child.rect.topleft = (child.rect.left,
                                      child.rect.top + self.scroll_step * (1 if up else -1))
