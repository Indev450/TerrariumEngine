from .label import Label


class ScrollableLabel(Label):
    
    def __init__(self,
                 scroll_step=10,
                 max_scroll=0,
                 text="",
                 parent=None,
                 children=None,
                 position_f=(0, 0),
                 size_f=(0.5, 0.5)):
        super().__init__(text=text,
                       parent=parent,
                       children=children,
                       position_f=position_f,
                       size_f=size_f)
        self.max_scroll = max_scroll
        self.scroll = 0
        self.scroll_step = scroll_step
        
    
    def on_scroll(self, position, up):
        if 0 <= (self.scroll + self.scroll_step * (-1 if up else 1)) <= self.max_scroll:
            self.scroll += self.scroll_step * (-1 if up else 1)
            for child in self.children:
                child.draw_pos = (child.draw_pos[0],
                                  child.draw_pos[1] + self.scroll_step * (1 if up else -1))
                child.rect.topleft = (child.rect.left,
                                      child.rect.top + self.scroll_step * (1 if up else -1))
