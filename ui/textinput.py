import pygame as pg


class TextInput:

    def __init__(self,
                 font,
                 on_return=None,
                 input_wait=0.05,
                 input_start_wait=0.5,
                 init_string="",
                 max_length=-1,
                 prompt="",
                 string_color="#FFFFFF",
                 prompt_color="#AAAAAA"):
        self.font = font
        
        self.on_return = on_return
        
        self.text = init_string
        self.prompt = prompt
        
        self.string_color = pg.Color(string_color)
        self.prompt_color = pg.Color(prompt_color)

        self.max_length = max_length
        
        self.surface = None
        
        self.cursor_pos = 0
        
        self.timer = 0
        self.time_to_wait = 0
        self.input_wait = input_wait
        self.input_start_wait = input_start_wait
        
        self.key_pressed = None
        self.capital = False
        
        self.last_text = None
        self.last_cursor_pos = None
        
        self.draw_cursor = True
        
        self.render_text()
    
    def render_text(self):
        text = self.text or self.prompt
        color = self.string_color if self.text else self.prompt_color
        
        # Preserve extra space for cursor
        self.surface = pg.Surface(self.font.size(text+' ')).convert_alpha()
        self.surface.fill(0)
        
        precursor_text = text[:self.cursor_pos]
        cursor_text = text[self.cursor_pos:self.cursor_pos+1]  # Slice helps to avoid IndexError
        postcursor_text = text[self.cursor_pos+1:]
        
        # If cursor is pointing on end of string, render it as a space
        cursor_surface = pg.Surface(self.font.size(cursor_text or ' '))
        cursor_surface.fill(color)
        
        # Render text before cursor
        self.surface.blit(self.font.render(precursor_text, True, color), (0, 0))
        
        if self.draw_cursor:
            # Render the cursor
            self.surface.blit(cursor_surface,
                              (self.font.size(precursor_text)[0], 0))
            # Render character on cursor with inverted color
            self.surface.blit(self.font.render(cursor_text, True, pg.Color('#FFFFFF') - color),
                              (self.font.size(precursor_text)[0], 0))
        else:
            self.surface.blit(self.font.render(cursor_text, True, color),
                              (self.font.size(precursor_text)[0], 0))

        # Render rest of the text
        self.surface.blit(self.font.render(postcursor_text, True, color),
                          (self.font.size(precursor_text)[0]+cursor_surface.get_width(), 0))
    
    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_RETURN, pg.K_BACKSPACE,
                             pg.K_DELETE, pg.K_LEFT, pg.K_RIGHT,
                             pg.K_UP, pg.K_DOWN):
                self.key_pressed = event.key
                
                # Type character immediatly and wait some time
                self.update(self.time_to_wait)
                self.time_to_wait = self.input_start_wait
            elif event.unicode:
                self.key_pressed = event.unicode
                
                # Type character immediatly and wait some time
                self.update(self.time_to_wait)
                self.time_to_wait = self.input_start_wait
        elif event.type == pg.KEYUP:
            if event.key in (pg.K_RETURN, pg.K_BACKSPACE,
                             pg.K_DELETE, pg.K_LEFT, pg.K_RIGHT,
                             pg.K_UP, pg.K_DOWN) and event.key == self.key_pressed:
                self.key_pressed = None
            elif event.unicode == self.key_pressed:
                self.key_pressed = None
        else:
            return event
    
    def update(self, dtime):
        self.timer += dtime
        
        if self.timer >= self.time_to_wait:
            self.timer = 0
            
            # Now wait for lesser time to keep typing text
            self.time_to_wait = self.input_wait

            if self.key_pressed == pg.K_RETURN:
                if self.on_return is not None:
                    self.on_return(self.text)
                    self.text = ""
                    self.cursor_pos = 0
            
            elif self.key_pressed == pg.K_BACKSPACE:
                if self.cursor_pos == 0:
                    return

                self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
            
            elif self.key_pressed == pg.K_DELETE:
                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            
            elif self.key_pressed == pg.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos-1)
            
            elif self.key_pressed == pg.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos+1)
            
            elif self.key_pressed == pg.K_UP:
                self.cursor_pos = 0
            
            elif self.key_pressed == pg.K_DOWN:
                self.cursor_pos = len(self.text)
            
            elif self.key_pressed is not None:
                newtext = self.text[:self.cursor_pos] + self.key_pressed + self.text[self.cursor_pos:]
                
                if self.max_length < 0 or not len(newtext) > self.max_length:
                    self.text = newtext
                    self.cursor_pos += 1
        
        if self.last_text != self.text or self.cursor_pos != self.last_cursor_pos:
            self.render_text()
            self.last_text = self.text
            self.last_cursor_pos = self.cursor_pos


if __name__ == "__main__":
    pg.init()

    # Create TextInput-object
    textinput = TextInput(pg.font.Font("dpcomic.ttf", 40), print, prompt="Type anything...")

    screen = pg.display.set_mode((1000, 200))
    
    clock = pg.time.Clock()

    while True:
        dtime = clock.tick(60) / 1000.0
        
        screen.fill((225, 225, 225))

        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                exit()
            
            textinput.handle_event(event)
        
        textinput.update(dtime)

        screen.blit(textinput.surface, (10, 10))

        pg.display.update()
