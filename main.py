import time
import pyglet
from pyglet.window import key, Window
from pyglet.image import load
import random
from cell import Cell

#TODO:
#settings menu
#writing solve times into a save file
#improve resolution scaling 

#-------------- constants and settings -----------------------------------
DARK_THEME = 0
GAME = ':)'
WIN = '^ - ^'
LOSS = '>_>'
PAUSE = "......time_stopped......."
#------------ Helper functions ----------------------------------------------

def get_neighbours(arr:list, i, j, radius=1):
    '''A function for finding all neighbouring elements in a matrix (2D array) including the element of origin.'''
    for y in range(i-radius, i + 1 + radius):
        for x in range(j-radius, j + 1 + radius):
            if y >= 0 and y < len(arr) and x >= 0 and x < len(arr[0]):
                yield arr[y][x]

def get_neighbours_index(arr:list, i, j, radius=1):
    '''A function for finding the indices of all neighbouring elements in a matrix (2D array) including the point of origin.'''
    for y in range(i-radius, i + 1 + radius):
        for x in range(j-radius, j + 1 + radius):
            if y >= 0 and y < len(arr) and x >= 0 and x < len(arr[0]):
                yield (y, x)

#---------------- The game --------------------------------------------------

game_window = Window(700, 700, "Minesweeper Pain(t)", resizable=True)
game_window.set_minimum_size(600, 450)

if DARK_THEME:
    pyglet.gl.glClearColor(100/255, 100/255, 100/255, 1)
else:
    pyglet.gl.glClearColor(173/255, 216/255, 230/255, 1)
batch = pyglet.graphics.Batch()
game_layer = pyglet.graphics.OrderedGroup(0)
menu_layer = pyglet.graphics.OrderedGroup(1)
menu_elements_layer = pyglet.graphics.OrderedGroup(2)

class SmileyFace(pyglet.sprite.Sprite):
    slightly_smiling_face_emoji = load("images/Slightly Smiling Face Emoji.png")
    smiling_emoji_with_eye_opened = load("images/Smiling Emoji with Eyes Opened.png")
    shyly_smiling_face_emoji = load("images/Shyly Smiling Face Emoji.png")
    loudly_crying_face_emoji = load("images/Loudly Crying Face Emoji.png")
    fearful_face_emoji = load("images/Fearful Face Emoji.png")
    cold_sweat_emoji = load("images/Cold Sweat Emoji.png")
    omg_face_emoji = load("images/OMG Face Emoji.png")
    for img in (slightly_smiling_face_emoji, smiling_emoji_with_eye_opened, shyly_smiling_face_emoji, loudly_crying_face_emoji, fearful_face_emoji, cold_sweat_emoji, omg_face_emoji):
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2

    def __init__(self, x, y, scale=1, batch=None, group=None):
        super().__init__(img = SmileyFace.slightly_smiling_face_emoji, x=x, y=y, batch=batch, group = group)
        self.scale = scale
    
    def reset(self):
        self.image = SmileyFace.slightly_smiling_face_emoji

    def win(self):
        self.image = random.choice((SmileyFace.smiling_emoji_with_eye_opened, SmileyFace.shyly_smiling_face_emoji))
    
    def loss(self):
        self.image = random.choice((SmileyFace.loudly_crying_face_emoji, SmileyFace.fearful_face_emoji, SmileyFace.cold_sweat_emoji, SmileyFace.omg_face_emoji))

class Button(pyglet.sprite.Sprite):
    '''Class for a button on the screen.'''
    def __init__(self, img, scale=1, *args, **kwargs):
        super().__init__(img=img, *args, **kwargs)
        self.scale = scale
        self.active = True
        game_window.push_handlers(self)

    def on_mouse_press(self, x, y, button, modifiers):
        '''Checks whether the button is pressed on each click.'''
        if self.active and self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            self.press()
    
    def press(self):
        '''A method that every inheretting class should define.
        Defines what the button does when pressed.'''
        raise NotImplementedError
            
    def activate(self):
        self.active = True
        self.visible = True

    def deactivate(self):
        self.active = False
        self.visible = False

class SettingsButton(Button):
    '''A button that opens the settings menu.'''
    button_image = load("images/settings_button.png")
    def __init__(self, scale=1, *args, **kwargs):
        super().__init__(img=SettingsButton.button_image, scale = scale, *args, **kwargs)
        self.active = True
        self.visible = True

    def press(self):
        '''When clicked, the button deactivates itself activates the menu.'''
        self.deactivate()
        settings_menu.activate()

class SettingsMenuCloseButton(Button):
    '''A button that closes the settings menu.'''
    button_image = load("images/close_button.png")
    def __init__(self, scale=1, opacity=255, *args, **kwargs):
        super().__init__(img=SettingsMenuCloseButton.button_image, scale = scale, *args, **kwargs)
        self.active = False
        self.visible = False
        self.opacity = opacity

    def press(self):
        '''When clicked, the button deactivates itself and the menu and activates the button that opens the menu.'''
        self.deactivate()
        settings_menu.deactivate()
        settings_button.activate()

class DifficultyButton(Button):
    '''A button that sets a specific difficulty'''
    button_images = {1:load("images/one.png"), 2:load("images/two.png"), 3:load("images/three.png")}
    def __init__(self, difficulty, scale=1, *args, **kwargs):
        super().__init__(img=DifficultyButton.button_images[difficulty], scale = scale, *args, **kwargs)
        self.difficulty = difficulty
        self.active = False
        self.visible = False

    def press(self):
        '''When clicked, the button the difficulty.'''   
        main_game.set_difficulty(self.difficulty)
        main_game.game_reset()
        main_game.on_resize(game_window.width, game_window.height)
        main_game.game_state = PAUSE
        Cell.open_soundeffect.play()

class SettingsMenu(pyglet.sprite.Sprite):
    '''An instance of an on-screen settings menu.'''
    #settings_menu_image = load("images/settings_menu.png")
    settings_menu_image = load("images/settings_menu_shadow_curved.png")
    settings_menu_image.anchor_x = settings_menu_image.width // 2
    settings_menu_image.anchor_y = settings_menu_image.height // 2

    def __init__(self, x, y, scale=1, batch=None, group=None):
        super().__init__(img=SettingsMenu.settings_menu_image, x=x, y=y, batch=batch, group=group)
        self.scale = scale
        self.opacity = 255 * 0.96
        self.active = False
        self.visible = False
        close_button_scale = 0.25
        self.close_button = SettingsMenuCloseButton(x=self.x + self.width // 2 - 200 * close_button_scale, y = self.y + self.height // 2 - 200 * close_button_scale, scale = close_button_scale, opacity = 255 * 0.8, batch=batch, group=menu_elements_layer)
        self.settings_label = pyglet.text.Label(text='Settings', font_name = "Сourier New", font_size = 40, x=self.x, y=self.y, anchor_x='center', batch=batch, group=menu_elements_layer, color=(0,0,0,255), bold = True)
        self.settings_label.visible = False
        self.difficulty_label = pyglet.text.Label(text='Difficulty:', font_name = "Consolas", font_size = 32, x=self.x, y=self.y, anchor_x='center', batch=batch, group=menu_elements_layer, color=(0,0,0,255))
        self.difficulty_label.visible = False
        self.difficulty_button_1 = DifficultyButton(1, x=200, y=200, batch = batch, group = menu_elements_layer)
        self.difficulty_button_2 = DifficultyButton(2, x=300, y=200, batch = batch, group = menu_elements_layer)
        self.difficulty_button_3 = DifficultyButton(3, x=400, y=200, batch = batch, group = menu_elements_layer)
        self.pressed_cells = []
        game_window.push_handlers(self)

    def activate(self):
        self.active = True
        self.visible = True
        self.old_game_state = main_game.game_state
        main_game.game_state = PAUSE
        self.close_button.activate()
        self.settings_label.visible = True
        self.difficulty_label.visible = True
        self.difficulty_button_1.activate()
        self.difficulty_button_2.activate()
        self.difficulty_button_3.activate()


    def deactivate(self):
        self.active = False
        self.visible = False
        main_game.game_state = self.old_game_state
        self.settings_label.visible = False
        self.difficulty_label.visible = False
        self.difficulty_button_1.deactivate()
        self.difficulty_button_2.deactivate()
        self.difficulty_button_3.deactivate()

    def on_resize(self, width, height):
        self.x = width // 2
        self.y = height // 2
        self.close_button.x = self.x + self.width / 2 - self.close_button.width 
        self.close_button.y = self.y + self.height / 2 - self.close_button.height
        self.settings_label.x = self.x
        self.settings_label.y = self.y + self.height * 0.35
        self.difficulty_label.x = self.x - self.width * 0.2
        self.difficulty_label.y = self.y + self.height * 0.175
        self.difficulty_button_1.x = self.x - self.width * 0.4
        self.difficulty_button_1.y = self.y
        self.difficulty_button_2.x = self.x - self.width * 0.3 
        self.difficulty_button_2.y = self.y 
        self.difficulty_button_3.x = self.x - self.width * 0.2 
        self.difficulty_button_3.y = self.y


class Timer(pyglet.text.Label):
    '''Game timer class.'''
    def __init__(self, *args, **kwargs):
        super(Timer, self).__init__('00:00', *args, **kwargs)
        
    def start_timer(self):
        self.reset_timer()
        self.__start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 0.5)

    def reset_timer(self):
        self.stop_timer()
        self.text = '00:00'

    def stop_timer(self):
        pyglet.clock.unschedule(self.update)

    def update(self, dt):
        cur_time =  time.time() - self.__start_time
        self.text = '{mins:0>2}:{secs:0>2}'.format(mins = int(cur_time / 60), secs = int(cur_time % 60))

#-----------------------------------------------------------------------------------------------#
settings_button = SettingsButton(x=0, y=game_window.width - 200 * 0.25, scale = 0.25, batch=batch, group=menu_layer)
settings_menu = SettingsMenu(game_window.width  // 2, game_window.height // 2, batch=batch, group=menu_layer)
#-----------------------------------------------------------------------------------------------#
Win = pyglet.media.load('sounds/win.wav')
class Main_game:
    '''Main game class'''
    
    def __init__(self):
        self.set_difficulty(3)
        self.cell_size = (min(game_window.width, game_window.height) - 100) // self.game_height
        self.game_offset_x = (game_window.width - self.game_width * self.cell_size) // 2
        self.game_state = GAME
        self.game_started = False
        self.game_timer = Timer(x=self.game_offset_x, y=57/70 * game_window.height, font_size=32, anchor_x='left', anchor_y='center', align='center', dpi = 150, color=(0,0,0,255), batch=batch, group=game_layer)
        self.smiley_face = SmileyFace( x=game_window.width // 2, y=game_window.height * 13/14, batch=batch, group=game_layer)
        self.flag_number_label = pyglet.text.Label(text=f'*:{self.mines_number}', font_name = 'Consolas', color=(0,0,0,255), bold=True, font_size=32, dpi=150, anchor_x='right', anchor_y='center', align='center', x=self.game_offset_x + self.game_width * self.cell_size, y= 57/70 * game_window.height, batch=batch, group=game_layer)

        self.minesweeper_matrix_clear()
        self.create_minefield()
        pyglet.clock.schedule_interval(self.update, 1/60)
        game_window.push_handlers(self)
    

    def minesweeper_matrix_clear(self):
        '''Create a matrix (2D list) which defines the minefield. '''
        self.minesweeper_matrix = [[0] * self.game_width for _ in range(self.game_height)]

    def create_minesweeper_matrix(self, x:int=None, y:int=None):
        mines_count = 0
        generator_matrix = [[0] * (self.game_width) for _ in range(self.game_height)] #a matrix with zeros and ones
        self.minesweeper_matrix = [[0] * self.game_width for _ in range(self.game_height)] #a matrix with numbers and 'b' (bomb)

        while mines_count < self.mines_number:           #generating a matrix with a needed number of mines. Clicked cell is never a mine + a few cells around it creatin an open space and making every gen playable
            row = random.choice(generator_matrix)
            row[random.randrange(len(row))] = 1 
            for i, j in get_neighbours_index(generator_matrix, y, x):
                generator_matrix[i][j] = 0       

            mines_count = sum(sum(row) for row in generator_matrix)
        generator_matrix.reverse()

        for i in range(self.game_height):                                #generating values matrix
            for j in range(self.game_width):
                if generator_matrix[i][j] == 1:
                    self.minesweeper_matrix[i][j] = 'b'
                else:
                    neighbouring_cells_sum = sum(get_neighbours(generator_matrix, i, j))
                    self.minesweeper_matrix[i][j] = neighbouring_cells_sum

 
    def create_minefield(self):
        '''Create a minefield comprised of sprites.'''
        self.cells = []
        for y in range(0, self.game_height * self.cell_size, self.cell_size):
            row = []
            for x in range(0, self.game_width * self.cell_size, self.cell_size):
                value = self.minesweeper_matrix[self.game_height - y//self.cell_size - 1][x//self.cell_size]
                row.append(Cell(value=value, x=x + self.game_offset_x, y=y, scale = self.cell_size / 30, batch=batch, group=game_layer)) 
            self.cells.append(row)

    def __in_minefield_range(self, x, y): return self.game_offset_x <= x < self.game_offset_x + self.cell_size * self.game_width and 0 <= y < self.cell_size * self.game_height

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.game_state == GAME and buttons == pyglet.window.mouse.LEFT:
            for row in self.cells:
                for cell in row:
                    cell.depress()
            if self.__in_minefield_range(x, y):
                cell = self.cells[y // self.cell_size][(x - self.game_offset_x) // self.cell_size]  
                cell.press()
            
    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == GAME and button == pyglet.window.mouse.LEFT:
            for row in self.cells:
                for cell in row:
                    cell.depress()
            if self.__in_minefield_range(x, y):
                cell = self.cells[y // self.cell_size][(x - self.game_offset_x) // self.cell_size]  
                cell.press()
        if self.game_state == LOSS and button == pyglet.window.mouse.LEFT:
            pyglet.clock.unschedule(self.blow_up_field)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.game_state == GAME:
            if button == pyglet.window.mouse.LEFT:
                if self.__in_minefield_range(x, y):
                    cell = self.cells[y // self.cell_size][(x - self.game_offset_x) // self.cell_size]  
                    cell.open(True)  #lmb - open cell                        
                    if not self.game_started:
                        self.game_start((x - self.game_offset_x) // self.cell_size, y // self.cell_size)               
            elif button == pyglet.window.mouse.RIGHT and self.__in_minefield_range(x, y):
                self.cells[y // self.cell_size][(x - self.game_offset_x) // self.cell_size].on_rmb() #rmb - switching between a closed cell, a flag or a question mark
            elif button == pyglet.window.mouse.MIDDLE and self.__in_minefield_range(x, y):
                neighbours = list(get_neighbours(self.cells, y // self.cell_size, (x - self.game_offset_x) // self.cell_size))
                rmb_states = [cell.rmb_state for cell in neighbours]
                if rmb_states.count('f') == self.cells[y // self.cell_size][(x - self.game_offset_x) // self.cell_size].value:
                    for cell in neighbours:
                        if not cell.openned and cell.rmb_state == 'x':
                            cell.open(True)



    def on_key_press(self, symbol, modifiers):
        if symbol == key.C:  #Cheats
            for row in self.cells:
                for cell in row:
                    if cell.value != 'b':
                        cell.open()
        elif symbol == key._1:
            self.set_difficulty(1)
            self.game_reset()
            self.on_resize(game_window.width, game_window.height)
        elif symbol == key._2:
            self.set_difficulty(2)
            self.game_reset()
            self.on_resize(game_window.width, game_window.height)
        elif symbol == key._3:
            self.set_difficulty(3)
            self.game_reset()
            self.on_resize(game_window.width, game_window.height)
        elif symbol == key.R: #reset the game
            self.game_reset()
        elif symbol == key.F11:
            game_window.set_fullscreen(1 - game_window.fullscreen)

    def on_resize(self, width, height):
        '''Resolution scaling method.'''
        indent = height / 4.5
        self.cell_size = int((height - indent) / self.game_height)
        if self.cell_size * self.game_width / 0.97 > width:
            self.cell_size = int(width / self.game_width * 0.97)


        scale = self.cell_size / 30
        self.game_offset_x = (width - self.game_width * self.cell_size) // 2
        #TODO: y_offset maybe? Haven't decided yet.

        #Setting the cells' xs and sizes to the calculated values
        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                cell.scale = scale
                cell.x = j * self.cell_size + self.game_offset_x
                cell.y = i * self.cell_size
                
        middle = height / 2 + self.game_height * self.cell_size / 2

        self.game_timer.x = 0.05 * width
        self.game_timer.y = middle

        self.game_timer.font_size = 32 * scale * self.font_scale

        self.smiley_face.x = game_window.width // 2
        self.smiley_face.y = middle
        self.smiley_face.scale = min(height, width) / 3100

        self.flag_number_label.x = width * 0.95
        self.flag_number_label.y =  middle

        self.flag_number_label.font_size = 32 * scale * self.font_scale
        settings_button.y = game_window.height - 200 * settings_button.scale

    def update(self, dt):
        '''Game state update method.'''
        openned_counter = 0
        flagged = 0
        if self.game_state == PAUSE:
            return
        if self.game_state == GAME:
            for i, row in enumerate(self.cells):
                for j, cell in enumerate(row):
                    if cell.openned:
                        openned_counter += 1
                        if cell.value == 'b':
                            self.game_state = LOSS
                            cell.value = 'bb'
                            self.bb_cell = (i, j)
                            return
                        elif cell.unchecked:
                            for y, x in get_neighbours_index(self.cells, i, j):
                                self.cells[y][x].open()
                                

                            cell.unchecked = False
                    elif cell.rmb_state == 'f':
                        flagged += 1
            self.flag_number_label.text = f'*:{max(0, self.mines_number - flagged)}'

            if openned_counter + self.mines_number == self.game_height * self.game_width:
                self.game_state = WIN
                Win.play()                
        else:                                                                      #game end
            self.show_field()
            if self.game_state == LOSS: #loss changes
                self.smiley_face.loss()
                self.blown_up_counter = 0
                pyglet.clock.schedule_interval(self.blow_up_field, 0.02)
            else: #win changes
                self.smiley_face.win()
            pyglet.clock.unschedule(self.update)
            self.game_timer.stop_timer()

    def game_start(self, x, y:tuple):
        "A method that starts the game on the first click."
        self.game_started = True
        self.game_timer.start_timer()
        self.create_minesweeper_matrix(x, y)
        self.create_minefield()
        self.cells[y][x].open()

    def game_reset(self):
        '''Resets the game by deleting sprites and setting game state booleans to the corrensponding values.'''
        self.game_state = GAME
        self.game_started = False
        self.smiley_face.reset()
        self.game_timer.reset_timer()

        for row in self.cells:
            for cell in row:
                cell.delete()

        pyglet.clock.unschedule(self.blow_up_field)
        self.minesweeper_matrix_clear()
        self.create_minefield()
        pyglet.clock.schedule_interval(self.update, 1/60)

    def set_difficulty(self, difficulty):
        '''Setting the difficulties between 1 (begginer) and 3 (expert) from minesweeper classic.'''
        if difficulty == 1:
            self.game_height = 8 #minefield height measured in cells
            self.game_width = 8 
            self.mines_number = 10 #target mines number
            self.font_scale = difficulty / 2
        elif difficulty == 2:
            self.game_height = 16
            self.game_width = 16
            self.mines_number = 40 
            self.font_scale = difficulty / 2
        elif difficulty == 3:
            self.game_height = 16
            self.game_width = 30
            self.mines_number = 99
            self.font_scale = difficulty / 2
        else:
            #TODO: implement custom boards
            raise NotImplementedError
        

    def show_field(self):
        for row in self.cells:
            for cell in row:
                cell.rmb_state = 'x'
                cell.open()
            
    def blow_up_field(self, dt):
        "Explosing the mines around the clicked mine in a circle."
        if self.blown_up_counter == 0:
            self.to_explode = []
            for i in range(1, max(self.game_width - self.bb_cell[1], self.bb_cell[1], self.game_height - self.bb_cell[0], self.bb_cell[0])):
                for neighbour in get_neighbours(self.cells, *self.bb_cell, radius = i):
                    if neighbour not in self.to_explode:
                        self.to_explode.append(neighbour)
        self.to_explode[self.blown_up_counter].explode()
        self.blown_up_counter += 1
        if self.blown_up_counter >= len(self.to_explode):
            pyglet.clock.unschedule(self.blow_up_field)

if __name__ == '__main__':
    
    main_game = Main_game()

    @game_window.event
    def on_draw():
        game_window.clear()
        batch.draw()

    pyglet.app.run()
