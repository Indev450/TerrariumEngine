import traceback

from config import getcfg


config = getcfg()


class Ticker:
    tick_time = config["tick.time"]
    
    def __init__(self):
        self.events = []
        self.timer = 0
    
    def update(self, dtime):
        self.timer += dtime
        
        if self.timer >= self.tick_time:
            i = 0
            
            while i < len(self.events):
                self.events[i].tick()
                
                if self.events[i].delete:
                    del self.events[i]
                    continue
                
                i += 1
            
            self.timer = 0
    
    def add_timer(self, ticks, callback, repeat=False):
        timer = TickTimer(ticks, callback, repeat)
        
        self.events.append(timer)
        
        return timer
    
    def del_timer(self, timer):
        try:
            self.events.remove(timer)
        except ValueError:
            traceback.print_stack()
            print('Warning: no such timer to delete')


class TickTimer:
    
    def __init__(self, ticks, callback, repeat=False):
        self.callback = callback
        self.ticks = ticks
        self.timer = 0
        self.repeat = repeat
        
        self.delete = False
    
    def tick(self):
        self.timer += 1
        
        if self.timer >= self.ticks:
            self.callback()
            self.timer = 0
            
            self.delete = not self.repeat
