import time
import pyglet
from pyglet.window import key, Window
from pyglet.resource import image
import random
from cell import Cell

#TODO:
#смайлик
#менюшки, кнопка
#запись рекордов по времени в сейв файл
#улучшение масштабирования
#три классические сложности
#-------------- Строковые константы ---------------------------------------
GAME = ':)'
WIN = '^ - ^'
LOSS = '>_>'
#---------------- Игра ---------------------------------------------------

def get_neighbours(arr:list, i, j, radius=1):
    '''функция для нахождения соседей (элементов) всех клеток в двухмерном списке(матрице)'''
    for y in range(i-radius, i + 1 + radius):
        for x in range(j-radius, j + 1 + radius):
            if y >= 0 and y < len(arr) and x >= 0 and x < len(arr[0]):
                yield arr[y][x]

def get_neighbours_index(arr:list, i, j, radius=1):
    '''функция для нахождения индексов соседей всех клеток в двухмерном списке(матрице)'''
    for y in range(i-radius, i + 1 + radius):
        for x in range(j-radius, j + 1 + radius):
            if y >= 0 and y < len(arr) and x >= 0 and x < len(arr[0]):
                yield (y, x)

#----------------------------------------------------------------------------

batch = pyglet.graphics.Batch()
game_window = Window(700, 700, "Сапёр", resizable=True)
game_window.set_minimum_size(320, 400)
pyglet.gl.glClearColor(173/255, 216/255, 230/255, 1)


class SmileyFace(pyglet.sprite.Sprite):
    slightly_smiling_face_emoji = image("Slightly Smiling Face Emoji.png")
    smiling_emoji_with_eye_opened = image("Smiling Emoji with Eyes Opened.png")
    shyly_smiling_face_emoji = image("Shyly Smiling Face Emoji.png")
    loudly_crying_face_emoji = image("Loudly Crying Face Emoji.png")
    fearful_face_emoji = image("Fearful Face Emoji.png")
    cold_sweat_emoji = image("Cold Sweat Emoji.png")
    omg_face_emoji = image("OMG Face Emoji.png")
    for img in (slightly_smiling_face_emoji, smiling_emoji_with_eye_opened, shyly_smiling_face_emoji, loudly_crying_face_emoji, fearful_face_emoji, cold_sweat_emoji, omg_face_emoji):
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2

    def __init__(self, x, y, scale=1, batch=None):
        super().__init__(img = SmileyFace.slightly_smiling_face_emoji, x=x, y=y, batch=batch)
        self.scale = scale
    
    def reset(self):
        self.image = SmileyFace.slightly_smiling_face_emoji

    def win(self):
        self.image = random.choice((SmileyFace.smiling_emoji_with_eye_opened, SmileyFace.shyly_smiling_face_emoji))
    
    def loss(self):
        self.image = random.choice((SmileyFace.loudly_crying_face_emoji, SmileyFace.fearful_face_emoji, SmileyFace.cold_sweat_emoji, SmileyFace.omg_face_emoji))

class Button(pyglet.sprite.Sprite):
    pass

class Menu(pyglet.sprite.Sprite):
    pass


class Timer(pyglet.text.Label):
    '''Таймер для игры'''
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

#класс игры в сапер
class Main_game:
    '''Основной класс игры'''
    win = pyglet.resource.media('win.wav')
    def __init__(self):
        self.set_difficulty(3)
        self.cell_size = (min(game_window.width, game_window.height) - 100) // self.game_height
        self.game_offset_x = (game_window.width - self.game_width * self.cell_size) // 2
        self.game_state = GAME
        self.game_started = False
        self.game_timer = Timer(x=self.game_offset_x, y=57/70 * game_window.height, font_size=32, dpi = 150, color=(0,0,0,255), batch=batch)
        self.smiley_face = SmileyFace( x=game_window.width // 2, y=game_window.height * 13/14, batch=batch)
        #self.game_state_label = pyglet.text.Label(text=GAME, font_name = 'Consolas', color=(0,0,0,255), bold=True, font_size=32, dpi=150, anchor_x='center', align='center', x=game_window.width // 2, y=game_window.height * 13/14, batch=batch) 
        self.flag_number_label = pyglet.text.Label(text=f'*:{self.mines_number}', font_name = 'Consolas', color=(0,0,0,255), bold=True, font_size=32, dpi=150, anchor_x='right', align='right', x=self.game_offset_x + self.game_width * self.cell_size, y= 57/70 * game_window.height, batch=batch)
        self.minesweeper_matrix_clear()
        self.create_minefield()
        pyglet.clock.schedule_interval(self.update, 1/60)
        game_window.push_handlers(self)
    

    def minesweeper_matrix_clear(self):
        '''создание двумерного списка(матрицы), в соответствии с которой создается "минное поле"'''
        self.minesweeper_matrix = [[0] * self.game_width for _ in range(self.game_height)]

    def create_minesweeper_matrix(self, x:int=None, y:int=None):
        mines_count = 0
        generator_matrix = [[0] * (self.game_width) for _ in range(self.game_height)] #матрица с нулями и единицами
        self.minesweeper_matrix = [[0] * self.game_width for _ in range(self.game_height)] #матрица с числами и 'b'

        while mines_count < self.mines_number:                       #генерация нужного количества мин, исключая точку клика
            row = random.choice(generator_matrix)
            row[random.randrange(len(row))] = 1 
            for i, j in get_neighbours_index(generator_matrix, y, x):
                generator_matrix[i][j] = 0       

            mines_count = sum(sum(row) for row in generator_matrix)
        generator_matrix.reverse()

        for i in range(self.game_height):                                #генерация матрицы со значениями клеток
            for j in range(self.game_width):
                if generator_matrix[i][j] == 1:
                    self.minesweeper_matrix[i][j] = 'b'
                else:
                    neighbouring_cells_sum = sum(get_neighbours(generator_matrix, i, j))
                    self.minesweeper_matrix[i][j] = neighbouring_cells_sum

 
    def create_minefield(self):
        '''создание 'минного поля' из спрайтов'''
        self.cells = []
        for y in range(0, self.game_height * self.cell_size, self.cell_size):
            row = []
            for x in range(0, self.game_width * self.cell_size, self.cell_size):
                value = self.minesweeper_matrix[self.game_height - y//self.cell_size - 1][x//self.cell_size]
                row.append(Cell(value=value, x=x + self.game_offset_x, y=y, scale = self.cell_size / 30, batch=batch)) 
            self.cells.append(row)

    def __in_minefield_range(self, x, y): return self.game_offset_x <= x < self.game_offset_x + self.cell_size * self.game_width and 0 <= y < self.cell_size * self.game_height

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == GAME:
            if button == pyglet.window.mouse.LEFT:
                if self.__in_minefield_range(x, y):
                    self.cells[y // self.cell_size][(x - self.game_offset_x) // self.cell_size].open()  #лкм - открытие клетки 
                    if not self.game_started:
                        self.game_start((x - self.game_offset_x) // self.cell_size, y // self.cell_size)               
            elif button == pyglet.window.mouse.RIGHT and self.__in_minefield_range(x, y):
                self.cells[y // self.cell_size][(x - self.game_offset_x) // self.cell_size].on_rmb() #правая кнопка - переключение между закрытой клеткой, флагом и знаком вопроса
            elif button == pyglet.window.mouse.MIDDLE and self.__in_minefield_range(x, y):
                neighbours = list(get_neighbours(self.cells, y // self.cell_size, (x - self.game_offset_x) // self.cell_size))
                rmb_states = [cell.rmb_state for cell in neighbours]
                if rmb_states.count('f') == self.cells[y // self.cell_size][(x - self.game_offset_x) // self.cell_size].value:
                    for cell in neighbours:
                        cell.open()
                    
        elif self.game_state == LOSS:
            pyglet.clock.unschedule(self.blow_up_field)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.C:  #читы - победа по нажатию кнопки
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
        elif symbol == key.R: #ресет игры
            self.game_reset()
        elif symbol == key.F11:
            game_window.set_fullscreen(1 - game_window.fullscreen)

    def on_resize(self, width, height):
        self.cell_size = (game_window.width - 100) // self.game_width
        if game_window.height - self.cell_size * self.game_height < 230:
            self.cell_size = (game_window.height - 230) // self.game_height

        scale = self.cell_size / 30
        self.game_offset_x = (game_window.width - self.game_width * self.cell_size) // 2
        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                cell.scale = scale
                cell.x = j * self.cell_size + self.game_offset_x
                cell.y = i * self.cell_size
                
        self.game_timer.x = self.game_offset_x
        self.game_timer.y = 55/70 * game_window.height
        self.game_timer.font_size = 32 * scale * self.font_scale

        self.smiley_face.x = game_window.width // 2
        self.smiley_face.y = game_window.height * 6/7
        self.smiley_face.scale = scale * 0.2

        self.flag_number_label.x = self.game_offset_x + self.game_width * self.cell_size
        self.flag_number_label.y =  55/70 * game_window.height
        self.flag_number_label.font_size = 32 * scale * self.font_scale
        

    def update(self, dt):
        '''метод обновления состояния игры'''
        openned_counter = 0
        flagged = 0
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
                Main_game.win.play()                
        else:                                                                      #конец игры
            self.show_field()
            if self.game_state == LOSS:
                self.smiley_face.loss()
                self.blown_up_counter = 0
                pyglet.clock.schedule_interval(self.blow_up_field, 0.02)
            else:
                self.smiley_face.win()
            pyglet.clock.unschedule(self.update)
            self.game_timer.stop_timer()

    def game_start(self, x, y:tuple):
        self.game_started = True
        self.game_timer.start_timer()
        self.create_minesweeper_matrix(x, y)
        self.create_minefield()
        self.cells[y][x].open()

    def game_reset(self):
        '''ресет игры'''
        self.game_state = GAME
        self.game_started = False
        self.smiley_face.reset()
        self.game_timer.reset_timer()
        pyglet.clock.unschedule(self.blow_up_field)
        self.minesweeper_matrix_clear()
        self.create_minefield()
        pyglet.clock.schedule_interval(self.update, 1/60)

    def set_difficulty(self, difficulty):
        if difficulty == 1:
            self.game_height = 8
            self.game_width = 8
            self.mines_number = 10 #целевое кол-во мин
            self.scale_ratio = 13
            self.font_scale = difficulty / 2
        elif difficulty == 2:
            self.game_height = 16
            self.game_width = 16
            self.mines_number = 40 #целевое кол-во мин
            self.scale_ratio = 24
            self.font_scale = difficulty / 2
        elif difficulty == 3:
            self.game_height = 16
            self.game_width = 30
            self.mines_number = 99
            self.scale_ratio = 35
            self.font_scale = difficulty / 2
            
        else:
            raise NotImplementedError
        

    def show_field(self):
        for row in self.cells:
            for cell in row:
                cell.rmb_state = 'x'
                cell.open()
            
    def blow_up_field(self, dt):
        if self.blown_up_counter == 0:
            self.to_explode = []
            for i in range(1, max(self.game_width, self.game_height)):
                for neighbour in get_neighbours(self.cells, *self.bb_cell, radius = i):
                    if neighbour not in self.to_explode:
                        self.to_explode.append(neighbour)

        self.to_explode[self.blown_up_counter].explode()
        self.blown_up_counter += 1
        if self.blown_up_counter >= self.game_height * self.game_width:
            pyglet.clock.unschedule(self.blow_up_field)

if __name__ == '__main__':
    main_game = Main_game()

    @game_window.event
    def on_draw():
        game_window.clear()
        batch.draw()

    pyglet.app.run()
